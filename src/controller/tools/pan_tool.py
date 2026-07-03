from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class PanTool(BaseTool):
    """Pan tool: middle-click style pan via left-click drag."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._panning = False
        self._last: QPointF | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.OpenHandCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        self._panning = True
        self._last = event.pos()
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouse_move(self, event, scene_pos: QPointF):
        if self._panning and self._last:
            delta = event.pos() - self._last
            self._last = event.pos()
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - int(delta.x()))
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - int(delta.y()))

    def mouse_release(self, event, scene_pos: QPointF):
        self._panning = False
        self._last = None
        self.view.setCursor(Qt.CursorShape.OpenHandCursor)

    def deactivate(self):
        self._panning = False
        super().deactivate()
