from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QCursor, QPen, QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget


class ZoomRubberBand(QWidget):
    """Overlay widget for zoom window rectangle — avoids Y-flip issues."""

    def __init__(self, view):
        super().__init__(view.viewport())
        self._view = view
        self._p1: QPoint | None = None
        self._p2: QPoint | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setGeometry(view.viewport().rect())
        self.hide()

    def set_points(self, p1: QPointF, p2: QPointF):
        """Set rectangle corners in scene coordinates."""
        self._p1 = self._view.mapFromScene(p1)
        self._p2 = self._view.mapFromScene(p2)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if self._p1 is None or self._p2 is None:
            return
        painter = QPainter(self)
        pen = QPen(QColor("#00FF88"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        x1, y1 = self._p1.x(), self._p1.y()
        x2, y2 = self._p2.x(), self._p2.y()
        rect = QRectF(
            min(x1, x2), min(y1, y2),
            abs(x2 - x1), abs(y2 - y1),
        )
        painter.drawRect(rect)
        painter.end()


class ZoomWinTool(BaseTool):
    """Window zoom: drag a rectangle to zoom in."""

    def __init__(self, view, document):
        super().__init__(view, document)
        self._start: QPointF | None = None
        self._rubber: ZoomRubberBand | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def activate(self):
        super().activate()
        self._rubber = ZoomRubberBand(self.view)

    def mouse_press(self, event, scene_pos: QPointF):
        self._start = scene_pos
        if self._rubber:
            self._rubber.show()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._rubber and self._start:
            self._rubber.set_points(self._start, scene_pos)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._rubber and self._start:
            x1, y1 = self._start.x(), self._start.y()
            x2, y2 = scene_pos.x(), scene_pos.y()
            w, h = abs(x2 - x1), abs(y2 - y1)
            self._rubber.hide()
            if w > 5 and h > 5:
                rect = QRectF(min(x1, x2), min(y1, y2), w, h)
                self.view.zoom_window(rect)
        self._start = None

    def deactivate(self):
        if self._rubber:
            self._rubber.hide()
            self._rubber.deleteLater()
            self._rubber = None
        self._start = None
        super().deactivate()
