from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor
from PySide6.QtWidgets import QGraphicsRectItem


class ZoomWinTool(BaseTool):
    """Window zoom: drag a rectangle to zoom in."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._start: QPointF | None = None
        self._rubber: QGraphicsRectItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        self._start = scene_pos
        self._rubber = QGraphicsRectItem()
        pen = QPen(QColor("#00FF88"))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidthF(0)
        self._rubber.setPen(pen)
        self._rubber.setZValue(10000)
        self.view.scene().addItem(self._rubber)

    def mouse_move(self, event, scene_pos: QPointF):
        if self._rubber and self._start:
            rect = QRectF(self._start, scene_pos).normalized()
            self._rubber.setRect(rect)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._rubber and self._start:
            rect = QRectF(self._start, scene_pos).normalized()
            self.view.scene().removeItem(self._rubber)
            self._rubber = None
            if rect.width() > 5 and rect.height() > 5:
                self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._start = None

    def deactivate(self):
        if self._rubber:
            self.view.scene().removeItem(self._rubber)
            self._rubber = None
        self._start = None
        super().deactivate()
