from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QRectF


class CadScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(QRectF(-10000, -10000, 20000, 20000))
