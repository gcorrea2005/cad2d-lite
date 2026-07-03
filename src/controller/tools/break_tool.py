from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class BreakTool(BaseTool):
    """Break a line at a point — split into two lines."""
    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                self._break_line(ent, pt)
                self.view.scene().removeItem(item)
                break

    def _break_line(self, line: Line, pt: Point):
        """Split line at point pt into two lines."""
        # Check pt is on the line (within tolerance)
        d_start = pt.distance_to(line.start)
        d_end = pt.distance_to(line.end)
        if d_start < 0.001 or d_end < 0.001:
            return  # at endpoint, nothing to break

        # Remove original
        self.document.remove_entity(line.uuid)

        # Create two new lines
        l1 = Line(line.start, pt, layer_name=line.layer_name, color=line.color)
        l2 = Line(pt, line.end, layer_name=line.layer_name, color=line.color)
        self.document.add_entity(l1)
        self.document.add_entity(l2)
