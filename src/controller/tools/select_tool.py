from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor, QPainter
from PySide6.QtWidgets import QGraphicsRectItem


class SelectTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._start_point: QPointF | None = None
        self._rubber_band: QGraphicsRectItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.ArrowCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        self._start_point = scene_pos
        self._rubber_band = QGraphicsRectItem()
        pen = QPen(QColor("#00AAFF"))
        pen.setStyle(Qt.PenStyle.DashLine)
        self._rubber_band.setPen(pen)
        self._rubber_band.setZValue(1000)
        self.view.scene().addItem(self._rubber_band)

    def mouse_move(self, event, scene_pos: QPointF):
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self._rubber_band.setRect(rect)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._rubber_band:
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
        self._start_point = None

    def deactivate(self):
        if self._rubber_band:
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
        self._start_point = None
