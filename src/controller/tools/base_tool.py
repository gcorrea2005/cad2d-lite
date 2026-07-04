from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QMouseEvent, QKeyEvent, QPen, QColor, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from src.model.entities.base import Point
from src.model.snap import SnapEngine, SnapType, SnapResult


class SnapIndicator(QGraphicsEllipseItem):
    """Visual indicator for snap points — green crosshair circle."""
    def __init__(self):
        super().__init__()
        self.setZValue(10000)
        self.setRect(-6, -6, 12, 12)
        pen = QPen(QColor("#00FF00"))
        pen.setWidthF(2)
        self.setPen(pen)
        self.setBrush(QColor(0, 255, 0, 50))
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
        # Pixel-based snap tolerance (converted to scene units dynamically)
        self._snap_pixels = 20

    @property
    def _current_color(self) -> str:
        """Read CECOLOR from sysvars (ACI index as string)."""
        try:
            return self.document.sysvars["CECOLOR"]
        except Exception:
            return "7"

    @property
    def _current_layer(self) -> str:
        """Current layer name from layer_manager."""
        return self.document.layer_manager.current_layer_name

    def activate(self):
        if self._snap_indicator.scene() is None:
            self.view.scene().addItem(self._snap_indicator)

    def deactivate(self):
        self._clear_snap_indicator()
        if self._snap_indicator.scene():
            self.view.scene().removeItem(self._snap_indicator)

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.ArrowCursor)

    def _pixel_to_scene_distance(self) -> float:
        """Convert snap_pixels to scene units based on current zoom level."""
        viewport = self.view.viewport()
        if viewport is None or viewport.width() == 0:
            return 15.0
        # Map a pixel distance to scene coordinates
        p1 = self.view.mapToScene(0, 0)
        p2 = self.view.mapToScene(self._snap_pixels, 0)
        dx = p2.x() - p1.x()
        return abs(dx)

    def _snap(self, scene_pos: QPointF) -> Point:
        """Snap the given scene position to nearby geometry. Returns snapped or original point."""
        cursor = Point(scene_pos.x(), scene_pos.y())
        # Update snap distance based on current zoom
        self._snap_engine.snap_distance = self._pixel_to_scene_distance()

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
