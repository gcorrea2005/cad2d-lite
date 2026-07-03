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

        # CAD convention: Y positive = UP. QGraphicsView default is Y-down, so flip.
        self.scale(1, -1)

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
        w = self.window()

        # Global hotkeys
        if event.key() == Qt.Key.Key_F8:
            if hasattr(w, '_toggle_ortho'):
                w._toggle_ortho()
                event.accept()
                return
        if event.key() == Qt.Key.Key_F9:
            if hasattr(w, '_toggle_snap'):
                w._toggle_snap()
                event.accept()
                return

        # Tool-switching shortcuts (like AutoCAD)
        key_map = {
            Qt.Key.Key_Escape: "select",
            Qt.Key.Key_L: "line",
            Qt.Key.Key_C: "circle",
            Qt.Key.Key_A: "arc",
            Qt.Key.Key_P: "polyline",
            Qt.Key.Key_R: "rectangle",
            Qt.Key.Key_T: "text",
            Qt.Key.Key_D: "dim",
            Qt.Key.Key_M: "move",
            Qt.Key.Key_O: "offset",
            Qt.Key.Key_X: "explode",
        }
        if (event.key() in key_map and
            not (event.modifiers() & Qt.KeyboardModifier.ControlModifier)):
            if hasattr(w, '_activate_tool'):
                w._activate_tool(key_map[event.key()])
                event.accept()
                return

        # Ctrl+Z / Ctrl+Y for undo/redo
        if event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if hasattr(w, '_on_undo'):
                w._on_undo()
                event.accept()
                return
        if event.key() == Qt.Key.Key_Y and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if hasattr(w, '_on_redo'):
                w._on_redo()
                event.accept()
                return

        # Forward to active tool (for tool-specific keys like Enter, Delete, etc.)
        if self.tool_manager and self.tool_manager._active_tool:
            self.tool_manager._active_tool.key_press(event)
            event.accept()
            return
        super().keyPressEvent(event)

    def zoom_extents(self):
        self._save_viewport()
        # Only consider entity items (skip grid)
        rect = self.scene().sceneRect()  # fallback
        items_rect = None
        for item in self.scene().items():
            if hasattr(item, 'entity'):
                br = item.sceneBoundingRect()
                if items_rect is None:
                    items_rect = br
                else:
                    items_rect = items_rect.united(br)
        if items_rect is not None and not items_rect.isEmpty():
            rect = items_rect
            # Add 10% margin
            rect.adjust(-rect.width() * 0.1, -rect.height() * 0.1,
                         rect.width() * 0.1, rect.height() * 0.1)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

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
