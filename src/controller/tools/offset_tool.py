"""OFFSET — cuadro distancia + click entidad + click lado."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


class OffsetTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._entity = None
        self._distance = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def activate(self):
        super().activate()
        self._echo("Select entity to offset")
        try:
            default = float(self.document.sysvars["OFFSETDIST"])
        except Exception:
            default = 1.0
        dist, ok = QInputDialog.getDouble(
            self.view, "Offset", "Offset distance:",
            default, 0.001, 10000, 4)
        if not ok:
            self.view.tool_manager.activate_tool("select")
            return
        self._distance = abs(dist)
        self.document.sysvars["OFFSETDIST"] = self._distance

    def _echo(self, msg: str):
        w = self.view.window()
        if hasattr(w, '_echo'):
            w._echo(msg)

    def mouse_press(self, event, scene_pos: QPointF):
        if self._distance is None:
            return

        if self._entity is None:
            # Pick entity — search in a small area around click
            r = 5.0  # search radius in scene units
            search_rect = QRectF(scene_pos.x() - r, scene_pos.y() - r, r * 2, r * 2)
            items = self.view.scene().items(search_rect, Qt.ItemSelectionMode.IntersectsItemShape)
            for item in items:
                ent = getattr(item, 'entity', None)
                if ent is None:
                    continue
                if isinstance(ent, (Line, Circle, Arc, Polyline)):
                    self._entity = ent
                    self._echo("Select side to offset")
                    return
        else:
            # Pick side and offset
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
            self._distance = None
            self._echo("Command:")

    def _side_sign(self, mid: Point, nx: float, ny: float, click: QPointF) -> float:
        to_click = Point(click.x() - mid.x, click.y() - mid.y)
        dot = to_click.x * nx + to_click.y * ny
        return 1.0 if dot > 0 else -1.0

    def _offset_line(self, line: Line, click_pos: QPointF):
        dx = line.end.x - line.start.x
        dy = line.end.y - line.start.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        nx = -dy / length
        ny = dx / length
        side = self._side_sign(line.midpoint(), nx, ny, click_pos)
        off = self._distance * side
        new_line = Line(
            Point(line.start.x + off * nx, line.start.y + off * ny),
            Point(line.end.x + off * nx, line.end.y + off * ny),
            layer_name=line.layer_name, color=line.color, linetype=line.linetype,
        )
        self.document.add_entity(new_line)
        self.view.scene().addItem(self._gfx(new_line))

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
        self.view.scene().addItem(self._gfx(new_circle))

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
        mid = Point((v0.x + v1.x) / 2, (v0.y + v1.y) / 2)
        side = self._side_sign(mid, nx, ny, click_pos)
        off = self._distance * side
        new_verts = [Point(v.x + off * nx, v.y + off * ny) for v in pl.vertices]
        new_pl = Polyline(new_verts, closed=pl.is_closed,
                          layer_name=pl.layer_name, color=pl.color,
                          linetype=pl.linetype)
        self.document.add_entity(new_pl)
        self.view.scene().addItem(self._gfx(new_pl))

    def _gfx(self, entity):
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
        self._distance = None
        super().deactivate()
