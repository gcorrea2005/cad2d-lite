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
from src.model.aci import aci_to_rgb


def _entity_color(entity) -> QColor:
    """Convert entity.color to QColor, supporting ACI indices and hex strings."""
    c = entity.color
    if isinstance(c, int):
        r, g, b = aci_to_rgb(c)
        return QColor(r, g, b)
    if isinstance(c, str) and c.isdigit():
        r, g, b = aci_to_rgb(int(c))
        return QColor(r, g, b)
    return QColor(c)


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
        color = _entity_color(self.entity)
        pen = QPen(color)
        pen.setWidthF(0)
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
        color = _entity_color(self.entity)
        pen = QPen(color)
        pen.setWidthF(0)
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
        color = _entity_color(self.entity)
        pen = QPen(color)
        pen.setWidthF(0)
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
        color = _entity_color(self.entity)
        pen = QPen(color)
        pen.setWidthF(0)
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
        color = _entity_color(self.entity)
        pen = QPen(color)
        pen.setWidthF(0)
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
        e = self.entity
        color = QColor(e.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)

        # Extension lines
        painter.drawLine(
            QPointF(e.def_point1.x, e.def_point1.y),
            QPointF(e.def_point1.x, e.text_position.y),
        )
        painter.drawLine(
            QPointF(e.def_point2.x, e.def_point2.y),
            QPointF(e.def_point2.x, e.text_position.y),
        )
        # Dimension line
        painter.drawLine(
            QPointF(e.def_point1.x, e.text_position.y),
            QPointF(e.def_point2.x, e.text_position.y),
        )
        # Text
        dist = e.measured_distance()
        font = painter.font()
        font.setPixelSize(10)
        painter.setFont(font)
        text = f"{dist:.2f}"
        mid_x = (e.def_point1.x + e.def_point2.x) / 2
        painter.drawText(QPointF(mid_x - 10, e.text_position.y - 2), text)


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
        color = _entity_color(self.entity)
        pen = QPen(color, 1)
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
