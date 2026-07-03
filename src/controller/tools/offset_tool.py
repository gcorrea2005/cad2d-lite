from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


class OffsetTool(BaseTool):
    """Offset a line or polyline by a distance."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._distance: float | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        if self._distance is None:
            dist, ok = QInputDialog.getDouble(
                self.view, "Offset", "Offset distance:",
                1.0, -10000, 10000, 4)
            if not ok:
                return
            self._distance = abs(dist)

        # Find entity under cursor
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                self._offset_line(ent, scene_pos)
            elif isinstance(ent, Polyline):
                self._offset_polyline(ent)
            break

    def _offset_line(self, line: Line, click_pos: QPointF):
        """Offset a single line perpendicular to its direction."""
        dx = line.end.x - line.start.x
        dy = line.end.y - line.start.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        # Perpendicular unit vector (rotate 90 deg counter-clockwise)
        nx = -dy / length
        ny = dx / length

        # Determine which side to offset based on click position
        mid = line.midpoint()
        to_click = Point(click_pos.x() - mid.x, click_pos.y() - mid.y)
        # Dot product with normal to determine side
        side = 1.0 if (to_click.x * nx + to_click.y * ny) > 0 else -1.0
        offset_dist = self._distance * side

        # Create parallel line
        new_start = Point(
            line.start.x + offset_dist * nx,
            line.start.y + offset_dist * ny)
        new_end = Point(
            line.end.x + offset_dist * nx,
            line.end.y + offset_dist * ny)

        new_line = Line(new_start, new_end, layer_name=line.layer_name, color=line.color)
        self.document.add_entity(new_line)

    def _offset_polyline(self, pl: Polyline):
        """Offset polyline — simplified: offset first segment only."""
        if len(pl.vertices) < 2:
            return
        # Build a temporary Line from first two vertices
        line = Line(pl.vertices[0], pl.vertices[1])
        # Use midpoint to determine offset direction (positive = outward)
        self._distance = self._distance or 1.0
        dx = line.end.x - line.start.x
        dy = line.end.y - line.start.y
        length = math.hypot(dx, dy)
        if length < 0.0001:
            return
        nx = -dy / length
        ny = dx / length

        new_verts = []
        for v in pl.vertices:
            new_verts.append(Point(
                v.x + self._distance * nx,
                v.y + self._distance * ny))

        new_pl = Polyline(new_verts, closed=pl.is_closed,
                          layer_name=pl.layer_name, color=pl.color)
        self.document.add_entity(new_pl)

    def deactivate(self):
        self._distance = None
        super().deactivate()
