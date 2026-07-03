from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
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


class ChamferTool(BaseTool):
    """Chamfer: bevel corner between two lines with two distances."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._d1: float = 1.0
        self._d2: float = 1.0
        self._line1: Line | None = None
        self._dists_set = False

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        if not self._dists_set:
            d1, ok = QInputDialog.getDouble(
                self.view, "Chamfer", "First chamfer distance:",
                1.0, 0.001, 10000, 4)
            if not ok:
                return
            d2, ok = QInputDialog.getDouble(
                self.view, "Chamfer", "Second chamfer distance:",
                d1, 0.001, 10000, 4)
            if not ok:
                return
            self._d1 = d1
            self._d2 = d2
            self._dists_set = True

        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Line):
                if self._line1 is None:
                    self._line1 = ent
                else:
                    self._do_chamfer(self._line1, ent)
                    self._line1 = None
                break

    def _do_chamfer(self, l1: Line, l2: Line):
        """Bevel corner between l1 and l2."""
        inter = _line_intersection(l1.start, l1.end, l2.start, l2.end)
        if inter is None:
            return

        # Direction vectors toward intersection
        def toward_inter(line: Line, inter: Point) -> tuple[float, float]:
            if line.start.distance_to(inter) < line.end.distance_to(inter):
                # Start is closer, direction from end toward start
                dx = line.start.x - line.end.x
                dy = line.start.y - line.end.y
            else:
                dx = line.end.x - line.start.x
                dy = line.end.y - line.start.y
            length = math.hypot(dx, dy)
            if length < 0.0001:
                return (0.0, 0.0)
            return (dx / length, dy / length)

        d1x, d1y = toward_inter(l1, inter)
        d2x, d2y = toward_inter(l2, inter)

        # Chamfer points (d1 distance from intersection along l1, d2 along l2)
        cp1 = Point(inter.x - d1x * self._d1, inter.y - d1y * self._d1)
        cp2 = Point(inter.x - d2x * self._d2, inter.y - d2y * self._d2)

        old1 = l1.to_dict()
        old2 = l2.to_dict()

        # Trim lines to chamfer points
        if l1.start.distance_to(inter) < l1.end.distance_to(inter):
            l1.start = cp1
        else:
            l1.end = cp1

        if l2.start.distance_to(inter) < l2.end.distance_to(inter):
            l2.start = cp2
        else:
            l2.end = cp2

        self.document.execute(ModifyEntityCommand(l1, old1, l1.to_dict()))
        self.document.execute(ModifyEntityCommand(l2, old2, l2.to_dict()))

        # Add chamfer line
        chamfer_line = Line(cp1, cp2, layer_name=l1.layer_name, color=l1.color)
        self.document.add_entity(chamfer_line)

    def deactivate(self):
        self._line1 = None
        self._dists_set = False
        super().deactivate()
