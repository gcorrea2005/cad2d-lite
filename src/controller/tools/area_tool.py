from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class AreaTool(BaseTool):
    """Area inquiry: click polygon vertices, show area and perimeter."""
    def __init__(self, view, document, echo_fn):
        super().__init__(view, document)
        self._points: list[Point] = []
        self._echo = echo_fn

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if event.button() == Qt.MouseButton.RightButton:
            if len(self._points) >= 3:
                self._calc_and_echo()
            self._points = []
            return
        self._points.append(pt)
        self._echo(f"Point {len(self._points)}: {pt.x:.4f}, {pt.y:.4f}")

    def key_press(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if len(self._points) >= 3:
                self._calc_and_echo()
            self._points = []
        elif event.key() == Qt.Key.Key_Escape:
            self._points = []
            self._echo("Command:")

    def _calc_and_echo(self):
        """Shoelace formula for polygon area."""
        n = len(self._points)
        area = 0.0
        perimeter = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self._points[i].x * self._points[j].y
            area -= self._points[j].x * self._points[i].y
            perimeter += self._points[i].distance_to(self._points[j])
        area = abs(area) / 2.0
        self._echo(f"Area = {area:.4f}  Perimeter = {perimeter:.4f}")
        self._echo("Command:")

    def deactivate(self):
        self._points = []
        super().deactivate()
