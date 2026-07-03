from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF, QRectF
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

        # Zoom history stack
        self._zoom_stack: list[QRectF] = []
        self._zoom_index: int = -1
        self._saving_zoom = True

    def wheelEvent(self, event: QWheelEvent):
        self._save_viewport()
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
            self._save_viewport()  # save after pan
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
        # Global hotkeys
        if event.key() == Qt.Key.Key_F8:
            # Ortho toggle
            w = self.window()
            if hasattr(w, '_toggle_ortho'):
                w._toggle_ortho()
                event.accept()
                return
        if event.key() == Qt.Key.Key_F9:
            # Snap toggle
            w = self.window()
            if hasattr(w, '_toggle_snap'):
                w._toggle_snap()
                event.accept()
                return
        # Forward to active tool
        if self.tool_manager and self.tool_manager._active_tool:
            self.tool_manager._active_tool.key_press(event)
            event.accept()
            return
        super().keyPressEvent(event)

    def zoom_extents(self):
        self._save_viewport()
        self.fitInView(self.scene().itemsBoundingRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_window(self, rect):
        self._save_viewport()
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def _save_viewport(self):
        """Push current viewport onto zoom history stack."""
        if not self._saving_zoom:
            return
        vr = self.viewport()
        if vr is None:
            return
        current = QRectF(
            self.mapToScene(vr.rect()).boundingRect()
        )
        # Truncate forward history if we're not at the end
        self._zoom_stack = self._zoom_stack[:self._zoom_index + 1]
        self._zoom_stack.append(current)
        self._zoom_index = len(self._zoom_stack) - 1
        # Cap at 50 entries
        if len(self._zoom_stack) > 50:
            self._zoom_stack = self._zoom_stack[-50:]
            self._zoom_index = len(self._zoom_stack) - 1

    def zoom_previous(self):
        """Restore previous zoom level."""
        if self._zoom_index <= 0:
            return
        self._zoom_index -= 1
        rect = self._zoom_stack[self._zoom_index]
        self._saving_zoom = False
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._saving_zoom = True
