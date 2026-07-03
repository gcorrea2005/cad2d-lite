from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


def _line_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    """Find intersection of two line segments (infinite lines). Returns None if parallel."""
    dx1 = a2.x - a1.x
    dy1 = a2.y - a1.y
    dx2 = b2.x - b1.x
    dy2 = b2.y - b1.y
    denom = dx1 * dy2 - dy1 * dx2
    if abs(denom) < 0.0001:
        return None
    t = ((b1.x - a1.x) * dy2 - (b1.y - a1.y) * dx2) / denom
    return Point(a1.x + t * dx1, a1.y + t * dy1)


class TrimTool(BaseTool):
    """Trim lines: click cutting edge, then click segment to trim."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._cutting_edge: Line | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                if self._cutting_edge is None:
                    # First click: select cutting edge
                    self._cutting_edge = ent
                else:
                    # Second click: trim this line to the cutting edge
                    self._trim_line(ent, self._cutting_edge)
                    self._cutting_edge = None
                break

    def _trim_line(self, line: Line, cutter: Line):
        """Trim line to cutter intersection. Remove the shorter side."""
        inter = _line_intersection(line.start, line.end, cutter.start, cutter.end)
        if inter is None:
            return

        old_dict = line.to_dict()
        # Determine which endpoint is closer to cutter = keep the other end
        d_start = line.start.distance_to(inter)
        d_end = line.end.distance_to(inter)

        # Keep the farther endpoint, set the other to intersection
        if d_start < d_end:
            line.start = inter
        else:
            line.end = inter

        self.document.execute(ModifyEntityCommand(line, old_dict, line.to_dict()))

    def deactivate(self):
        self._cutting_edge = None
        super().deactivate()
