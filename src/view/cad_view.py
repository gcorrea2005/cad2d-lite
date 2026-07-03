from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QWheelEvent, QMouseEvent


class CadView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(Qt.GlobalColor.black)

        self._zoom_factor = 1.15
        self._panning = False
        self._last_pan_point = QPointF()
        self.tool_manager = None

        self.setMouseTracking(True)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale(self._zoom_factor, self._zoom_factor)
        else:
            self.scale(1 / self._zoom_factor, 1 / self._zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        if self.tool_manager and self.tool_manager._active_tool:
            if event.button() == Qt.MouseButton.LeftButton:
                scene_pos = self.mapToScene(event.pos())
                self.tool_manager._active_tool.mouse_press(event, scene_pos)
                event.accept()
                return
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_point = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.tool_manager and self.tool_manager._active_tool:
            scene_pos = self.mapToScene(event.pos())
            self.tool_manager._active_tool.mouse_move(event, scene_pos)
            # Update status bar coordinates
            if hasattr(self, '_status_callback') and self._status_callback:
                self._status_callback(scene_pos)
        if self._panning:
            delta = event.position() - self._last_pan_point
            self._last_pan_point = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        # Forward release to tool
        if self.tool_manager and self.tool_manager._active_tool:
            scene_pos = self.mapToScene(event.pos())
            self.tool_manager._active_tool.mouse_release(event, scene_pos)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        # Forward key events to active tool
        if self.tool_manager and self.tool_manager._active_tool:
            self.tool_manager._active_tool.key_press(event)
            event.accept()
            return
        super().keyPressEvent(event)

    def zoom_extents(self):
        self.fitInView(self.scene().itemsBoundingRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_window(self, rect):
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
