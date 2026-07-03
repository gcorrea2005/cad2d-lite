from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.arc import Arc
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


def _line_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    dx1 = a2.x - a1.x
    dy1 = a2.y - a1.y
    dx2 = b2.x - b1.x
    dy2 = b2.y - b1.y
    denom = dx1 * dy2 - dy1 * dx2
    if abs(denom) < 0.0001:
        return None
    t = ((b1.x - a1.x) * dy2 - (b1.y - a1.y) * dx2) / denom
    return Point(a1.x + t * dx1, a1.y + t * dy1)


class FilletTool(BaseTool):
    """Fillet: round corner between two lines with an arc of given radius."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._radius: float = 1.0
        self._line1: Line | None = None
        self._radius_set = False

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        if not self._radius_set:
            r, ok = QInputDialog.getDouble(
                self.view, "Fillet", "Fillet radius:",
                1.0, 0.001, 10000, 4)
            if not ok:
                return
            self._radius = r
            self._radius_set = True

        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                if self._line1 is None:
                    self._line1 = ent
                else:
                    self._do_fillet(self._line1, ent)
                    self._line1 = None
                break

    def _do_fillet(self, l1: Line, l2: Line):
        """Round corner between l1 and l2 with an arc."""
        inter = _line_intersection(l1.start, l1.end, l2.start, l2.end)
        if inter is None:
            return  # parallel lines

        # Unit direction vectors
        d1x = l1.end.x - l1.start.x
        d1y = l1.end.y - l1.start.y
        len1 = math.hypot(d1x, d1y)
        if len1 < 0.0001:
            return
        d1x /= len1
        d1y /= len1

        d2x = l2.end.x - l2.start.x
        d2y = l2.end.y - l2.start.y
        len2 = math.hypot(d2x, d2y)
        if len2 < 0.0001:
            return
        d2x /= len2
        d2y /= len2

        # Angle between direction vectors
        dot = d1x * d2x + d1y * d2y
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)
        if angle < 0.001:
            return  # parallel

        # Distance from intersection to tangent points
        half_angle = angle / 2.0
        dist = self._radius / math.tan(half_angle)

        # Tangent points (toward intersection)
        tp1 = Point(inter.x - d1x * dist, inter.y - d1y * dist)
        tp2 = Point(inter.x - d2x * dist, inter.y - d2y * dist)

        # Trim lines to tangent points
        # Determine which endpoint is closer to intersection for each line
        old1 = l1.to_dict()
        old2 = l2.to_dict()

        if l1.start.distance_to(inter) < l1.end.distance_to(inter):
            l1.start = tp1
        else:
            l1.end = tp1

        if l2.start.distance_to(inter) < l2.end.distance_to(inter):
            l2.start = tp2
        else:
            l2.end = tp2

        self.document.execute(ModifyEntityCommand(l1, old1, l1.to_dict()))
        self.document.execute(ModifyEntityCommand(l2, old2, l2.to_dict()))

        # Create arc between tangent points
        # Arc center is where perpendiculars from tangent points meet
        # Simplified: compute start/end angles from intersection
        start_angle = math.atan2(tp1.y - inter.y, tp1.x - inter.x)
        end_angle = math.atan2(tp2.y - inter.y, tp2.x - inter.x)

        # Compute actual arc center
        mid_angle = (start_angle + end_angle) / 2.0
        center_dist = self._radius / math.sin(half_angle)
        center = Point(
            inter.x + center_dist * math.cos(mid_angle),
            inter.y + center_dist * math.sin(mid_angle))

        # Recompute angles from center
        start_angle = math.atan2(tp1.y - center.y, tp1.x - center.x)
        end_angle = math.atan2(tp2.y - center.y, tp2.x - center.x)

        # Ensure counter-clockwise
        if end_angle < start_angle:
            end_angle += 2 * math.pi

        arc = Arc(center, self._radius, start_angle, end_angle,
                  layer_name=l1.layer_name, color=l1.color)
        self.document.add_entity(arc)

    def deactivate(self):
        self._line1 = None
        self._radius_set = False
        super().deactivate()
