from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor, QMouseEvent, QKeyEvent, QPen, QColor, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from src.model.entities.base import Point
from src.model.snap import SnapEngine, SnapType, SnapResult


class SnapIndicator(QGraphicsEllipseItem):
    """Visual indicator for snap points — small yellow circle."""
    def __init__(self):
        super().__init__()
        self.setZValue(10000)
        self.setRect(-5, -5, 10, 10)
        pen = QPen(QColor("#FFFF00"))
        pen.setWidthF(2)
        self.setPen(pen)
        self.setBrush(QColor(255, 255, 0, 60))
        self.hide()


class BaseTool:
    def __init__(self, view, document):
        self.view = view
        self.document = document
        self._snap_engine = SnapEngine(snap_distance=15.0)
        self._active_snaps: set[SnapType] = {
            SnapType.ENDPOINT, SnapType.MIDPOINT, SnapType.CENTER,
            SnapType.NEAREST,
        }
        self._snap_indicator = SnapIndicator()
        self._last_snap: SnapResult | None = None

    def activate(self):
        if self._snap_indicator.scene() is None:
            self.view.scene().addItem(self._snap_indicator)

    def deactivate(self):
        self._clear_snap_indicator()
        if self._snap_indicator.scene():
            self.view.scene().removeItem(self._snap_indicator)

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.ArrowCursor)

    def _snap(self, scene_pos: QPointF) -> Point:
        """Snap the given scene position to nearby geometry. Returns snapped or original point."""
        cursor = Point(scene_pos.x(), scene_pos.y())
        result = self._snap_engine.find_snap(
            cursor, self.document.entities, self._active_snaps
        )
        if result:
            self._last_snap = result
            self._snap_indicator.setPos(QPointF(result.point.x, result.point.y))
            self._snap_indicator.show()
            return result.point
        else:
            self._last_snap = None
            self._snap_indicator.hide()
            return cursor

    def _clear_snap_indicator(self):
        self._snap_indicator.hide()
        self._last_snap = None

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF): ...
    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF): ...
    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF): ...
    def key_press(self, event: QKeyEvent): ...
