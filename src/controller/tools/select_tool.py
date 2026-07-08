from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsRectItem
from src.model.entities.base import Point
import math


GRIP_COLD   = QColor("#4488FF")
GRIP_HOT    = QColor("#FF6600")
GRIP_ACTIVE = QColor("#FF0000")
GRIP_PEN    = QColor("#0000FF")

GRIP_PX  = 3.0
HOVER_PX = 12.0


class SelectTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._start_point: QPointF | None = None
        self._rubber_band: QGraphicsRectItem | None = None
        self._grips: list[QGraphicsRectItem] = []
        self._dragging_grip: int | None = None
        self._hovered_grip: int | None = None
        self._grip_points: list[Point] = []
        self._grip_entity = None
        self._grip_mode = "stretch"
        self._drag_anchor: Point | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.ArrowCursor)

    # ═══════════════════════════════════════════════════════════
    #  Mouse events
    # ═══════════════════════════════════════════════════════════

    def mouse_press(self, event, scene_pos: QPointF):
        if self._grips:
            for i, grip in enumerate(self._grips):
                if grip.contains(self.view.mapFromScene(scene_pos)):
                    self._dragging_grip = i
                    self._grip_mode = "stretch"
                    self._drag_anchor = self._grip_points[0]
                    self._paint_grips(hot=i)
                    return
            self._clear_grips()

        items = self.view.scene().items(scene_pos)
        entity_items = [it for it in items if hasattr(it, 'entity')]

        if entity_items:
            self._clear_selection()
            item = entity_items[0]
            self._highlight_item(item, True)
            self.view._selected_uuids = [item.entity.uuid]
            self._show_grips(item)
        else:
            self._clear_selection()
            self.view._selected_uuids = []
            self._clear_grips()
            self._start_point = scene_pos
            self._rubber_band = QGraphicsRectItem()
            pen = QPen(QColor("#00AAFF"))
            pen.setStyle(Qt.PenStyle.DashLine)
            self._rubber_band.setPen(pen)
            self._rubber_band.setZValue(1000)
            self.view.scene().addItem(self._rubber_band)

    def mouse_move(self, event, scene_pos: QPointF):
        # Hover snap
        if self._dragging_grip is None and self._grips and not self._rubber_band:
            pixel_w = self.view.transform().m11()
            threshold = HOVER_PX / pixel_w if pixel_w > 0 else HOVER_PX
            nearest = None
            best_dist = threshold
            for i, gp in enumerate(self._grip_points):
                d = math.hypot(scene_pos.x() - gp.x, scene_pos.y() - gp.y)
                if d < best_dist:
                    best_dist = d
                    nearest = i
            if nearest != self._hovered_grip:
                self._hovered_grip = nearest
                self._paint_grips(hot=nearest if nearest is not None else -1)
            return

        # Grip drag
        if self._dragging_grip is not None and self._grip_entity and self._grip_points:
            self._handle_grip_drag(scene_pos)
            return

        # Rubber band
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self._rubber_band.setRect(rect)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._dragging_grip is not None:
            self._dragging_grip = None
            self._drag_anchor = None
            self._grip_mode = "stretch"
            return
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
            self._clear_selection()
            selected = []
            for item in self.view.scene().items(rect):
                if hasattr(item, 'entity') and hasattr(item.entity, 'uuid'):
                    self._highlight_item(item, True)
                    selected.append(item.entity.uuid)
            self.view._selected_uuids = selected
        self._start_point = None

    # ═══════════════════════════════════════════════════════════
    #  Key events
    # ═══════════════════════════════════════════════════════════

    def key_press(self, event):
        key = event.key()

        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            uuids = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
            for uuid in uuids:
                if uuid in self.document._entities:
                    self.document.remove_entity(uuid)
            for item in list(self.view.scene().items()):
                if hasattr(item, 'entity') and item.entity.uuid in uuids:
                    self.view.scene().removeItem(item)
            self.view._selected_uuids = []
            self._clear_grips()
            return

        if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._dragging_grip is not None:
                modes = ["stretch", "move", "rotate", "scale"]
                idx = modes.index(self._grip_mode)
                self._grip_mode = modes[(idx + 1) % len(modes)]
                if self._dragging_grip == 0 and len(self._grip_points) > 1:
                    self._drag_anchor = self._grip_points[1]
                else:
                    self._drag_anchor = self._grip_points[0]
                return

    # ═══════════════════════════════════════════════════════════
    #  Grip drag dispatch
    # ═══════════════════════════════════════════════════════════

    def _handle_grip_drag(self, scene_pos: QPointF):
        ent = self._grip_entity
        gp = self._grip_points
        idx = self._dragging_grip
        pt = self._snap(scene_pos)

        if self._grip_mode == "stretch":
            self._do_stretch(ent, idx, pt, gp)
        elif self._grip_mode == "move":
            self._do_move(ent, pt)
        elif self._grip_mode == "rotate":
            self._do_rotate(ent, pt, gp, idx)
        elif self._grip_mode == "scale":
            self._do_scale(ent, pt, gp, idx)

        gfx = self._find_gfx(ent)
        if gfx:
            gfx.prepareGeometryChange()
            gfx.update()

        self._clear_grips()
        if gfx:
            self._show_grips(gfx)

    # ═══════════════════════════════════════════════════════════
    #  Stretch  (move the gripped point)
    # ═══════════════════════════════════════════════════════════

    def _do_stretch(self, ent, idx, pt, gp):
        t = type(ent).__name__

        if t == "Line":
            if idx == 0:        ent.start = pt
            elif idx == 1:      ent.end = pt
            elif idx == 2:      # midpoint → move whole line
                dx, dy = pt.x - gp[2].x, pt.y - gp[2].y
                ent.start = Point(ent.start.x + dx, ent.start.y + dy)
                ent.end   = Point(ent.end.x   + dx, ent.end.y   + dy)

        elif t == "Circle":
            if idx == 0:        ent.center = pt
            else:               ent.radius = ent.center.distance_to(pt)

        elif t == "Arc":
            if idx == 0:        ent.center = pt
            elif idx == 1:      ent.start_angle = math.atan2(pt.y - ent.center.y, pt.x - ent.center.x)
            elif idx == 2:      ent.end_angle   = math.atan2(pt.y - ent.center.y, pt.x - ent.center.x)
            elif idx == 3:      ent.radius = ent.center.distance_to(pt)

        elif t == "Polyline":
            n = len(ent.vertices)
            if idx < n:         # vertex grip
                ent.vertices[idx] = pt
            else:               # midpoint grip → move segment
                seg = idx - n
                v1 = ent.vertices[seg]
                v2 = ent.vertices[(seg + 1) % n] if ent.is_closed and seg == n - 1 else ent.vertices[seg + 1] if seg + 1 < n else v1
                dx, dy = pt.x - gp[idx].x, pt.y - gp[idx].y
                ent.vertices[seg] = Point(v1.x + dx, v1.y + dy)
                nxt = (seg + 1) % n if ent.is_closed and seg == n - 1 else seg + 1
                if nxt < n:
                    ent.vertices[nxt] = Point(v2.x + dx, v2.y + dy)

        elif t == "Ellipse":
            if idx == 0:        ent.center = pt
            elif idx == 1:      # major axis endpoint
                ent.major_axis = pt
            else:               # quadrant → adjust ratio
                ang = ent.angle
                dx = pt.x - ent.center.x
                dy = pt.y - ent.center.y
                proj = dx * math.cos(ang) + dy * math.sin(ang)
                perp = abs(-dx * math.sin(ang) + dy * math.cos(ang))
                maj = ent.major_radius
                ent.ratio = perp / maj if maj > 0.001 else ent.ratio

        elif t in ("PointEntity", "TextEntity"):
            # Single grip → move
            if t == "PointEntity":   ent.position = pt
            else:                    ent.position = pt

    # ═══════════════════════════════════════════════════════════
    #  Move  (displace whole entity)
    # ═══════════════════════════════════════════════════════════

    def _do_move(self, ent, pt):
        dx = dy = 0.0
        if self._drag_anchor:
            dx = pt.x - self._drag_anchor.x
            dy = pt.y - self._drag_anchor.y
        self._drag_anchor = pt

        t = type(ent).__name__

        if t == "Line":
            ent.start = Point(ent.start.x + dx, ent.start.y + dy)
            ent.end   = Point(ent.end.x   + dx, ent.end.y   + dy)
        elif t == "Circle":
            ent.center = Point(ent.center.x + dx, ent.center.y + dy)
        elif t == "Arc":
            ent.center = Point(ent.center.x + dx, ent.center.y + dy)
        elif t == "Polyline":
            for i in range(len(ent.vertices)):
                ent.vertices[i] = Point(ent.vertices[i].x + dx, ent.vertices[i].y + dy)
        elif t == "Ellipse":
            ent.center     = Point(ent.center.x + dx, ent.center.y + dy)
            ent.major_axis = Point(ent.major_axis.x + dx, ent.major_axis.y + dy)
        elif t == "PointEntity":
            ent.position = Point(ent.position.x + dx, ent.position.y + dy)
        elif t == "TextEntity":
            ent.position = Point(ent.position.x + dx, ent.position.y + dy)

    # ═══════════════════════════════════════════════════════════
    #  Rotate  (around opposite grip)
    # ═══════════════════════════════════════════════════════════

    def _do_rotate(self, ent, pt, gp, idx):
        center = gp[1] if idx == 0 else gp[0]
        angle = math.atan2(pt.y - center.y, pt.x - center.x)

        def _rot(p):
            dx, dy = p.x - center.x, p.y - center.y
            return Point(center.x + dx * math.cos(angle) + dy * math.sin(angle),
                         center.y - dx * math.sin(angle) + dy * math.cos(angle))

        t = type(ent).__name__

        if t == "Line":
            ent.start = _rot(ent.start)
            ent.end   = _rot(ent.end)
        elif t == "Circle":
            ent.center = center
        elif t == "Arc":
            ent.center = center
        elif t == "Polyline":
            for i in range(len(ent.vertices)):
                ent.vertices[i] = _rot(ent.vertices[i])
        elif t == "Ellipse":
            ent.center     = center
            ent.major_axis = _rot(ent.major_axis)
        elif t in ("PointEntity", "TextEntity"):
            if t == "PointEntity":   ent.position = _rot(ent.position)
            else:                    ent.position = _rot(ent.position)

    # ═══════════════════════════════════════════════════════════
    #  Scale  (from opposite grip)
    # ═══════════════════════════════════════════════════════════

    def _do_scale(self, ent, pt, gp, idx):
        base = gp[1] if idx == 0 else gp[0]
        old_d = base.distance_to(gp[idx])
        new_d = base.distance_to(pt)
        f = new_d / old_d if old_d > 0.001 else 1.0

        def _scl(p):
            return Point(base.x + (p.x - base.x) * f, base.y + (p.y - base.y) * f)

        t = type(ent).__name__

        if t == "Line":
            ent.start = _scl(ent.start)
            ent.end   = _scl(ent.end)
        elif t == "Circle":
            ent.radius *= f
        elif t == "Arc":
            ent.radius *= f
        elif t == "Polyline":
            for i in range(len(ent.vertices)):
                ent.vertices[i] = _scl(ent.vertices[i])
        elif t == "Ellipse":
            ent.major_axis = _scl(ent.major_axis)
            # ratio stays the same
        elif t in ("PointEntity", "TextEntity"):
            if t == "PointEntity":   ent.position = _scl(ent.position)
            else:                    ent.position = _scl(ent.position)

    # ═══════════════════════════════════════════════════════════
    #  Grip creation
    # ═══════════════════════════════════════════════════════════

    def _show_grips(self, item):
        self._clear_grips()
        ent = item.entity
        self._grip_entity = ent
        self._grip_points = []

        pixel_w = self.view.transform().m11()
        size = GRIP_PX / pixel_w if pixel_w > 0 else 4.0
        t = type(ent).__name__

        if t == "Line":
            pts = [Point(ent.start.x, ent.start.y),
                   Point(ent.end.x,   ent.end.y),
                   Point((ent.start.x + ent.end.x) / 2, (ent.start.y + ent.end.y) / 2)]

        elif t == "Circle":
            pts = [Point(ent.center.x, ent.center.y)]
            r = ent.radius
            for a in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                pts.append(Point(ent.center.x + r * math.cos(a), ent.center.y + r * math.sin(a)))

        elif t == "Arc":
            pts = [Point(ent.center.x, ent.center.y),
                   ent.start_point(),
                   ent.end_point(),
                   ent.midpoint()]

        elif t == "Polyline":
            pts = [Point(v.x, v.y) for v in ent.vertices]
            # Add midpoints
            n = len(ent.vertices)
            for i in range(n):
                nxt = (i + 1) % n
                if i < n - 1 or ent.is_closed:
                    a, b = ent.vertices[i], ent.vertices[nxt]
                    pts.append(Point((a.x + b.x) / 2, (a.y + b.y) / 2))

        elif t == "Ellipse":
            pts = [Point(ent.center.x, ent.center.y),
                   Point(ent.major_axis.x, ent.major_axis.y)]
            ang = ent.angle
            r_maj = ent.major_radius
            r_min = ent.minor_radius
            for a_off in [math.pi / 2, math.pi, 3 * math.pi / 2]:
                a = ang + a_off
                px = ent.center.x + r_maj * math.cos(a)
                py = ent.center.y + r_min * math.sin(a)
                pts.append(Point(px, py))

        elif t == "PointEntity":
            pts = [Point(ent.position.x, ent.position.y)]

        elif t == "TextEntity":
            pts = [Point(ent.position.x, ent.position.y)]

        else:
            return

        self._grip_points = pts
        for p in pts:
            grip = QGraphicsRectItem(QRectF(p.x - size, p.y - size, size * 2, size * 2))
            grip.setPen(QPen(GRIP_PEN, 1))
            grip.setBrush(QBrush(GRIP_COLD))
            grip.setZValue(2000)
            self.view.scene().addItem(grip)
            self._grips.append(grip)

    # ═══════════════════════════════════════════════════════════
    #  Grip painting helpers
    # ═══════════════════════════════════════════════════════════

    def _paint_grips(self, hot: int = -1):
        if hot >= 0 and hot < len(self._grips):
            self._grips[hot].setBrush(QBrush(GRIP_HOT))
            self._grips[hot].setPen(QPen(QColor("#CC4400"), 2))
        for i, g in enumerate(self._grips):
            if i != hot:
                g.setBrush(QBrush(GRIP_COLD))
                g.setPen(QPen(GRIP_PEN, 1))

    def _find_gfx(self, ent):
        for item in self.view.scene().items():
            if hasattr(item, 'entity') and item.entity is ent:
                return item
        return None

    def _clear_grips(self):
        self._hovered_grip = None
        for g in self._grips:
            self.view.scene().removeItem(g)
        self._grips = []
        self._grip_points = []
        self._grip_entity = None
        self._dragging_grip = None

    def _highlight_item(self, item, selected: bool):
        item.setSelected(selected)

    def _clear_selection(self):
        self._clear_grips()
        for item in list(self.view.scene().items()):
            if hasattr(item, 'entity'):
                item.setSelected(False)
        if hasattr(self.view, '_selected_uuids'):
            self.view._selected_uuids = []

    def deactivate(self):
        if self._rubber_band:
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
        self._start_point = None
        self._clear_grips()
