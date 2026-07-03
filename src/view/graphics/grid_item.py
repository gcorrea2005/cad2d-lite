from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPen, QPainter


class GridItem(QGraphicsItem):
    def __init__(self, scene_rect: QRectF, spacing: float = 10.0):
        super().__init__()
        self._rect = scene_rect
        self._spacing = spacing
        self.setZValue(-100)

    def boundingRect(self):
        return self._rect

    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(Qt.GlobalColor.darkGray)
        pen.setWidthF(0)
        painter.setPen(pen)

        left = int(self._rect.left() / self._spacing) * self._spacing
        top = int(self._rect.top() / self._spacing) * self._spacing

        x = left
        while x <= self._rect.right():
            painter.drawLine(x, self._rect.top(), x, self._rect.bottom())
            x += self._spacing

        y = top
        while y <= self._rect.bottom():
            painter.drawLine(self._rect.left(), y, self._rect.right(), y)
            y += self._spacing
