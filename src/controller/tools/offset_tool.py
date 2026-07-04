"""OFFSET tool — create parallel copy of entity at distance, picking side."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


class OffsetTool(BaseTool):
    """Offset entity: pick entity, enter/confirm distance, click side."""

    def __init__(self, view, document):
        super().__init__(view, document)
        self._distance: float | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Read OFFSETDIST from SETVAR if not set
        if self._distance is None:
            try:
                self._distance = float(self.document.sysvars["OFFSETDIST"])
            except Exception:
                pass

        if self._distance is None or self._distance == 0:
            dist, ok = QInputDialog.getDouble(
                self.view, "Offset", "Offset distance:",
                1.0, 0.001, 10000, 4)
            if not ok:
                return
            self._distance = abs(dist)
            # Save to SETVAR
            try:
                self.document.sysvars["OFFSETDIST"] = self._distance
            except Exception:
                pass

        # Find entity under cursor
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                self._offset_line(ent, scene_pos)
            elif isinstance(ent, Circle):
                self._offset_circle(ent, scene_pos)
            elif isinstance(ent, Arc):
                self._offset_circle(ent, scene_pos)  # same logic
            elif isinstance(ent, Polyline):
                self._offset_polyline(ent, scene_pos)
            break

    def _side_sign(self, mid: Point, normal: Point, click: QPointF) -> float:
        """Determine offset direction: +1 or -1 based on click side."""
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
        """Offset circle: change radius by distance, direction based on click."""
        to_center = Point(click_pos.x() - circle.center.x, click_pos.y() - circle.center.y)
        dist_to_center = math.hypot(to_center.x, to_center.y)
        if dist_to_center < 0.0001:
            return
        # If click is outside the circle, grow radius; inside, shrink
        side = 1.0 if dist_to_center > circle.radius else -1.0
        new_r = circle.radius + self._distance * side
        if new_r <= 0:
            return  # can't shrink to nothing
        new_circle = Circle(circle.center, new_r,
                            layer_name=circle.layer_name, color=circle.color,
                            linetype=circle.linetype)
        self.document.add_entity(new_circle)
        self.view.scene().addItem(self._make_gfx(new_circle))

    def _offset_polyline(self, pl: Polyline, click_pos: QPointF):
        """Offset polyline: compute normal from first segment, determine side from click."""
        if len(pl.vertices) < 2:
            return
        # Use first segment for normal direction
        v0, v1 = pl.vertices[0], pl.vertices[1]
        dx = v1.x - v0.x
        dy = v1.y - v0.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        nx = -dy / length
        ny = dx / length
        normal = Point(nx, ny)

        # Determine side from click relative to first segment midpoint
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
        """Create appropriate GfxItem for the entity."""
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
        self._distance = None
        super().deactivate()
