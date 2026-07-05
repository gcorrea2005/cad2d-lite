"""OFFSET tool — parallel copy of entity: pick entity, pick side. Distance from OFFSETDIST."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class OffsetTool(BaseTool):
    """Offset entity at OFFSETDIST: click entity, click side."""

    def __init__(self, view, document):
        super().__init__(view, document)
        self._entity = None   # entity to offset
        self._step = 0        # 0=pick entity, 1=pick side

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Read distance from OFFSETDIST
        try:
            distance = float(self.document.sysvars["OFFSETDIST"])
        except Exception:
            distance = 1.0
        if distance <= 0:
            distance = 1.0

        if self._step == 0:
            # Pick entity
            items = self.view.scene().items(scene_pos)
            for item in items:
                if not hasattr(item, 'entity'):
                    continue
                ent = item.entity
                if isinstance(ent, (Line, Circle, Arc, Polyline)):
                    self._entity = ent
                    self._distance = distance
                    self._step = 1
                    return
        else:
            # Pick side and offset
            if self._entity is None:
                self._step = 0
                return
            ent = self._entity
            if isinstance(ent, Line):
                self._offset_line(ent, scene_pos)
            elif isinstance(ent, Circle):
                self._offset_circle(ent, scene_pos)
            elif isinstance(ent, Arc):
                self._offset_circle(ent, scene_pos)
            elif isinstance(ent, Polyline):
                self._offset_polyline(ent, scene_pos)
            self._entity = None
            self._step = 0

    def _side_sign(self, mid: Point, normal: Point, click: QPointF) -> float:
        to_click = Point(click.x() - mid.x, click.y() - mid.y)
        dot = to_click.x * normal.x + to_click.y * normal.y
        return 1.0 if dot > 0 else -1.0

    def _offset_line(self, line: Line, click_pos: QPointF):
        dx = line.end.x - line.start.x
        dy = line.end.y - line.start.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        nx = -dy / length
        ny = dx / length
        normal = Point(nx, ny)
        side = self._side_sign(line.midpoint(), normal, click_pos)
        off = self._distance * side

        new_line = Line(
            Point(line.start.x + off * nx, line.start.y + off * ny),
            Point(line.end.x + off * nx, line.end.y + off * ny),
            layer_name=line.layer_name, color=line.color, linetype=line.linetype,
        )
        self.document.add_entity(new_line)
        self.view.scene().addItem(self._make_gfx(new_line))

    def _offset_circle(self, circle: Circle, click_pos: QPointF):
        to_center = Point(click_pos.x() - circle.center.x, click_pos.y() - circle.center.y)
        dist_to_center = math.hypot(to_center.x, to_center.y)
        if dist_to_center < 0.0001:
            return
        side = 1.0 if dist_to_center > circle.radius else -1.0
        new_r = circle.radius + self._distance * side
        if new_r <= 0:
            return
        new_circle = Circle(circle.center, new_r,
                            layer_name=circle.layer_name, color=circle.color,
                            linetype=circle.linetype)
        self.document.add_entity(new_circle)
        self.view.scene().addItem(self._make_gfx(new_circle))

    def _offset_polyline(self, pl: Polyline, click_pos: QPointF):
        if len(pl.vertices) < 2:
            return
        v0, v1 = pl.vertices[0], pl.vertices[1]
        dx = v1.x - v0.x
        dy = v1.y - v0.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        nx = -dy / length
        ny = dx / length
        normal = Point(nx, ny)
        mid = Point((v0.x + v1.x) / 2, (v0.y + v1.y) / 2)
        side = self._side_sign(mid, normal, click_pos)
        off = self._distance * side

        new_verts = [Point(v.x + off * nx, v.y + off * ny) for v in pl.vertices]
        new_pl = Polyline(new_verts, closed=pl.is_closed,
                          layer_name=pl.layer_name, color=pl.color,
                          linetype=pl.linetype)
        self.document.add_entity(new_pl)
        self.view.scene().addItem(self._make_gfx(new_pl))

    def _make_gfx(self, entity):
        from src.view.graphics.entity_items import (
            GfxLineItem, GfxCircleItem, GfxPolylineItem,
        )
        if isinstance(entity, Line):
            return GfxLineItem(entity)
        elif isinstance(entity, Circle):
            return GfxCircleItem(entity)
        elif isinstance(entity, Polyline):
            return GfxPolylineItem(entity)
        return None

    def deactivate(self):
        self._entity = None
        self._step = 0
        super().deactivate()
