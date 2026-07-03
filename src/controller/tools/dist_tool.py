from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class DistTool(BaseTool):
    """Distance inquiry: two clicks, shows distance in command line."""
    def __init__(self, view, document, echo_fn):
        super().__init__(view, document)
        self._p1: Point | None = None
        self._echo = echo_fn

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._p1 is None:
            self._p1 = pt
            self._echo(f"First point: {pt.x:.4f}, {pt.y:.4f}")
        else:
            dist = self._p1.distance_to(pt)
            dx = pt.x - self._p1.x
            dy = pt.y - self._p1.y
            self._echo(f"Distance = {dist:.4f}  "
                       f"Delta X = {dx:.4f}  Delta Y = {dy:.4f}")
            self._echo("Command:")
            self._p1 = None

    def deactivate(self):
        self._p1 = None
        super().deactivate()
