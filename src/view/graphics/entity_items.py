from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPen, QColor, QPainter
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from src.model.entities.point_entity import PointEntity
from src.model.entities.base import Point
from src.model.aci import aci_to_rgb
from src.model.linetype_defs import get_qt_dash_pattern


def _entity_color(entity) -> QColor:
    """Convert entity.color to QColor, supporting ACI indices and hex strings."""
    c = entity.color
    if isinstance(c, int):
        r, g, b = aci_to_rgb(c)
        return QColor(r, g, b)
    if isinstance(c, str) and c.isdigit():
        r, g, b = aci_to_rgb(int(c))
        return QColor(r, g, b)
    if isinstance(c, str) and c.upper() in ("BYLAYER", "BYBLOCK"):
        return QColor(255, 255, 255)  # default white
    qc = QColor(c)
    if not qc.isValid():
        return QColor(255, 255, 255)  # fallback
    return qc


def _entity_pen(entity, ltscale: float = 1.0) -> QPen:
    """Create QPen with entity color + linetype dash pattern."""
    pen = QPen(_entity_color(entity))
    pen.setWidthF(0)  # cosmetic pen (1px regardless of zoom)
    dash = get_qt_dash_pattern(entity.linetype, ltscale)
    if dash:
        pen.setDashPattern(dash)
    return pen


import math


class GfxLineItem(QGraphicsItem):
    def __init__(self, entity: Line):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self.entity.start.x, self.entity.start.y),
            QPointF(self.entity.end.x, self.entity.end.y),
        )


class GfxCircleItem(QGraphicsItem):
    def __init__(self, entity: Circle):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        r = self.entity.radius
        c = self.entity.center
        painter.drawEllipse(QPointF(c.x, c.y), r, r)


class GfxArcItem(QGraphicsItem):
    def __init__(self, entity: Arc):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        e = self.entity
        # QPainter.drawArc uses 1/16 degree units, and spans counter-clockwise
        span_angle = int(-math.degrees(e.end_angle - e.start_angle) * 16)
        start_angle = int(-math.degrees(e.start_angle) * 16)
        rect = QRectF(
            QPointF(e.center.x - e.radius, e.center.y - e.radius),
            QPointF(e.center.x + e.radius, e.center.y + e.radius),
        )
        painter.drawArc(rect, start_angle, span_angle)


class GfxPolylineItem(QGraphicsItem):
    def __init__(self, entity: Polyline):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        verts = self.entity.vertices
        for i in range(len(verts) - 1):
            painter.drawLine(
                QPointF(verts[i].x, verts[i].y),
                QPointF(verts[i + 1].x, verts[i + 1].y),
            )
        if self.entity.is_closed and len(verts) >= 2:
            painter.drawLine(
                QPointF(verts[-1].x, verts[-1].y),
                QPointF(verts[0].x, verts[0].y),
            )


class GfxTextItem(QGraphicsItem):
    def __init__(self, entity: TextEntity):
        super().__init__()
        self.entity = entity
        self.setZValue(0)
        # Counter-flip to compensate view's Y-up transform
        from PySide6.QtGui import QTransform
        self.setTransform(QTransform.fromScale(1, -1))

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        font = painter.font()
        # Use pixel size for consistent readability
        font.setPixelSize(max(8, int(self.entity.height * 40)))
        painter.setFont(font)
        painter.drawText(
            QPointF(self.entity.position.x, self.entity.position.y),
            self.entity.content,
        )


class GfxDimensionItem(QGraphicsItem):
    def __init__(self, entity: Dimension):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        r = QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))
        # Ensure minimum size for hit detection
        if r.width() < 1:
            r.adjust(-0.5, 0, 0.5, 0)
        if r.height() < 1:
            r.adjust(0, -0.5, 0, 0.5)
        return r

    def paint(self, painter: QPainter, option, widget=None):
        import math
        e = self.entity
        pen = _entity_pen(e)
        painter.setPen(pen)

        p1, p2 = e.def_point1, e.def_point2
        tp = e.text_position
        dist = e.measured_distance()
        arrow_size = 6  # DIMASZ equivalent

        # ── Helper: draw arrowhead ──
        def draw_arrow(tip_x: float, tip_y: float, ang: float):
            a1 = ang + math.radians(160)
            a2 = ang - math.radians(160)
            pts = [
                QPointF(tip_x, tip_y),
                QPointF(tip_x + arrow_size * math.cos(a1), tip_y + arrow_size * math.sin(a1)),
                QPointF(tip_x + arrow_size * math.cos(a2), tip_y + arrow_size * math.sin(a2)),
            ]
            painter.save()
            painter.setBrush(pen.color())
            painter.drawPolygon(pts)
            painter.restore()

        if e.dim_type == "aligned":
            # Angle of the line connecting the two points
            ang = math.atan2(p2.y - p1.y, p2.x - p1.x)
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            perp_x, perp_y = -sin_a, cos_a

            # Compute offset from text_position
            mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
            ext_len = (tp.x - mid.x) * perp_x + (tp.y - mid.y) * perp_y
            if abs(ext_len) < 5:
                ext_len = 15

            # Extension lines
            ext1_end = Point(p1.x + perp_x * ext_len, p1.y + perp_y * ext_len)
            ext2_end = Point(p2.x + perp_x * ext_len, p2.y + perp_y * ext_len)
            painter.drawLine(QPointF(p1.x, p1.y), QPointF(ext1_end.x, ext1_end.y))
            painter.drawLine(QPointF(p2.x, p2.y), QPointF(ext2_end.x, ext2_end.y))

            # Dimension line
            painter.drawLine(QPointF(ext1_end.x, ext1_end.y), QPointF(ext2_end.x, ext2_end.y))

            # Arrowheads
            dir_ang = ang if cos_a >= 0 else ang + math.pi
            draw_arrow(ext1_end.x, ext1_end.y, dir_ang + math.pi)
            draw_arrow(ext2_end.x, ext2_end.y, dir_ang)

            # Text centered on dim line
            mid_x = (ext1_end.x + ext2_end.x) / 2
            mid_y = (ext1_end.y + ext2_end.y) / 2
            font = painter.font()
            font.setPixelSize(11)
            painter.setFont(font)
            text = f"{dist:.2f}"
            painter.save()
            painter.translate(QPointF(mid_x, mid_y))
            if cos_a < 0:
                painter.rotate(math.degrees(ang) + 180)
            else:
                painter.rotate(math.degrees(ang))
            # Counter-flip for text readability
            painter.scale(1, -1)
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(text)
            painter.drawText(QPointF(-tw / 2, 6), text)
            painter.restore()

        elif e.dim_type == "radius" or e.dim_type == "diameter":
            center, edge = p1, p2
            ang = math.atan2(edge.y - center.y, edge.x - center.x)

            # Leader line from edge to text
            painter.drawLine(QPointF(center.x, center.y), QPointF(edge.x, edge.y))

            # Arrow at edge point
            draw_arrow(edge.x, edge.y, ang)

            # Text at text_position offset
            font = painter.font()
            font.setPixelSize(11)
            painter.setFont(font)
            prefix = "⌀ " if e.dim_type == "diameter" else "R "
            text = f"{prefix}{dist:.2f}"
            painter.save()
            painter.translate(QPointF(tp.x, tp.y))
            painter.scale(1, -1)
            painter.drawText(QPointF(0, -4), text)
            painter.restore()

        elif e.dim_type == "angular":
            # p1=vertex, p2=point on arc, tp=text position
            vertex, arc_pt = p1, p2
            # Angle from vertex to arc_pt
            ang1 = math.atan2(arc_pt.y - vertex.y, arc_pt.x - vertex.x)
            # Use tp as the second angle direction
            ang2 = math.atan2(tp.y - vertex.y, tp.x - vertex.x)
            # Draw arc between the two angles
            r = vertex.distance_to(arc_pt) * 0.6
            # Draw rays
            painter.drawLine(QPointF(vertex.x, vertex.y),
                           QPointF(vertex.x + r * 2 * math.cos(ang1), vertex.y + r * 2 * math.sin(ang1)))
            painter.drawLine(QPointF(vertex.x, vertex.y),
                           QPointF(vertex.x + r * 2 * math.cos(ang2), vertex.y + r * 2 * math.sin(ang2)))
            # Draw arc
            start_deg = math.degrees(ang1)
            end_deg = math.degrees(ang2)
            span = end_deg - start_deg
            if span > 180: span -= 360
            if span < -180: span += 360
            arc_rect = QRectF(vertex.x - r, vertex.y - r, r * 2, r * 2)
            painter.drawArc(arc_rect, int(start_deg * 16), int(span * 16))
            # Text
            font = painter.font()
            font.setPixelSize(11)
            painter.setFont(font)
            angle_deg = abs(span)
            text = f"{angle_deg:.1f}°"
            mid_ang = ang1 + math.radians(span / 2)
            tx = vertex.x + r * 1.3 * math.cos(mid_ang)
            ty = vertex.y + r * 1.3 * math.sin(mid_ang)
            painter.drawText(QPointF(tx, ty), text)

        else:
            # Linear H/V
            if abs(p2.x - p1.x) >= abs(p2.y - p1.y):
                # Horizontal
                dim_y = tp.y
                painter.drawLine(QPointF(p1.x, p1.y), QPointF(p1.x, dim_y))
                painter.drawLine(QPointF(p2.x, p2.y), QPointF(p2.x, dim_y))
                painter.drawLine(QPointF(p1.x, dim_y), QPointF(p2.x, dim_y))
                left, right = (p1.x, p2.x) if p1.x < p2.x else (p2.x, p1.x)
                draw_arrow(left, dim_y, math.pi)
                draw_arrow(right, dim_y, 0)
                mid_x = (p1.x + p2.x) / 2
                font = painter.font()
                font.setPixelSize(11)
                painter.setFont(font)
                text = f"{dist:.2f}"
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(text)
                painter.save()
                painter.translate(QPointF(mid_x - tw / 2, dim_y))
                painter.scale(1, -1)
                painter.drawText(QPointF(0, 4), text)
                painter.restore()
            else:
                # Vertical
                dim_x = tp.x
                painter.drawLine(QPointF(p1.x, p1.y), QPointF(dim_x, p1.y))
                painter.drawLine(QPointF(p2.x, p2.y), QPointF(dim_x, p2.y))
                painter.drawLine(QPointF(dim_x, p1.y), QPointF(dim_x, p2.y))
                bottom, top = (p1.y, p2.y) if p1.y < p2.y else (p2.y, p1.y)
                draw_arrow(dim_x, bottom, -math.pi / 2)
                draw_arrow(dim_x, top, math.pi / 2)
                mid_y = (p1.y + p2.y) / 2
                font = painter.font()
                font.setPixelSize(11)
                painter.setFont(font)
                text = f"{dist:.2f}"
                painter.save()
                painter.translate(QPointF(dim_x, mid_y))
                painter.scale(1, -1)
                painter.rotate(-90)
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(text)
                painter.drawText(QPointF(-4, tw / 2), text)
                painter.restore()


class GfxPointItem(QGraphicsItem):
    """Point entity with AutoCAD-style PDMODE/PDSIZE rendering."""

    # PDMODE style flags
    _STYLE_DOT = 0
    _STYLE_NONE = 1
    _STYLE_CROSS = 2
    _STYLE_X = 3
    _STYLE_TICK = 4

    _SHAPE_CIRCLE = 32
    _SHAPE_SQUARE = 64

    def __init__(self, entity: PointEntity):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        size = self._point_size()
        half = size / 2 + 3
        return QRectF(
            self.entity.position.x - half,
            self.entity.position.y - half,
            half * 2, half * 2,
        )

    def paint(self, painter: QPainter, option, widget=None):
        pen = _entity_pen(self.entity)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        p = self.entity.position
        x, y = p.x, p.y
        size = self._point_size()
        half = size / 2

        # Read PDMODE from sysvars (default 3 = X)
        pdmode = self._get_pdmode()
        style = pdmode & 0x0F    # 0-4
        shape = pdmode & 0xF0    # 0, 32, 64, 96

        # ── Draw center style ──
        if style == self._STYLE_DOT:
            painter.drawPoint(QPointF(x, y))
        elif style == self._STYLE_NONE:
            pass  # invisible
        elif style == self._STYLE_CROSS:
            painter.drawLine(QPointF(x - half, y), QPointF(x + half, y))
            painter.drawLine(QPointF(x, y - half), QPointF(x, y + half))
        elif style == self._STYLE_X:
            painter.drawLine(QPointF(x - half, y - half), QPointF(x + half, y + half))
            painter.drawLine(QPointF(x + half, y - half), QPointF(x - half, y + half))
        elif style == self._STYLE_TICK:
            painter.drawLine(QPointF(x, y - half), QPointF(x, y + half))
        else:
            painter.drawPoint(QPointF(x, y))

        # ── Draw surrounding shape ──
        if shape & self._SHAPE_CIRCLE:
            painter.drawEllipse(QPointF(x, y), half, half)
        if shape & self._SHAPE_SQUARE:
            painter.drawRect(QRectF(x - half, y - half, size, size))

    def _point_size(self) -> float:
        """Compute point size from PDSIZE + viewport scale."""
        pdsize = self._get_pdsize()
        if pdsize == 0:
            # 5% of viewport height in scene units
            view = self.scene().views()[0] if self.scene() and self.scene().views() else None
            if view:
                top_left = view.mapToScene(0, 0)
                bot = view.mapToScene(0, int(view.viewport().height() * 0.05))
                return abs(bot.y() - top_left.y())
            return 5.0
        return pdsize

    def _get_pdmode(self) -> int:
        """Read PDMODE from document sysvars, default 3 (X)."""
        try:
            ent = self.entity
            if hasattr(ent, '_document') and ent._document:
                return int(ent._document.sysvars["PDMODE"])
        except Exception:
            pass
        return 3

    def _get_pdsize(self) -> float:
        """Read PDSIZE from document sysvars, default 0 (5% viewport)."""
        try:
            ent = self.entity
            if hasattr(ent, '_document') and ent._document:
                return float(ent._document.sysvars["PDSIZE"])
        except Exception:
            pass
        return 0
