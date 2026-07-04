from PySide6.QtWidgets import QGraphicsView, QWidget
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QPainter, QPaintEvent


class CrosshairOverlay(QWidget):
    """Transparent overlay that paints only the crosshair + pickbox — no scene repaint."""

    def __init__(self, view: QGraphicsView):
        super().__init__(view.viewport())
        self._view = view
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setGeometry(view.viewport().rect())

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        vp = self._view.viewport()
        if vp is None:
            painter.end()
            return

        scene_pos = getattr(self._view, '_cursor_scene_pos', QPointF(0, 0))
        cursor_vp = self._view.mapFromScene(scene_pos)

        cross_color = QColor("#FFFFFF")
        cross_color.setAlpha(180)
        pickbox_color = QColor("#00FF00")
        pickbox_color.setAlpha(220)

        w, h = vp.width(), vp.height()
        cx, cy = cursor_vp.x(), cursor_vp.y()
        clip_margin = 4

        # ── Full-screen crosshair ──
        pen = QPen(cross_color, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(int(cx), clip_margin, int(cx), h - clip_margin)
        painter.drawLine(clip_margin, int(cy), w - clip_margin, int(cy))

        # ── Pickbox (8×8 px square at intersection) ──
        pickbox_size = 8
        half = pickbox_size // 2
        pen = QPen(pickbox_color, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(
            int(cx - half), int(cy - half),
            pickbox_size, pickbox_size,
        )

        painter.end()


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

        # CAD convention: Y positive = UP
        self.scale(1, -1)

        self._zoom_factor = 1.15
        self._panning = False
        self._last_pan_point = QPointF()
        self.tool_manager = None

        self.setMouseTracking(True)

        # Crosshair cursor tracking
        self._cursor_scene_pos = QPointF(0, 0)

        # Overlay for crosshair (lightweight, no scene repaint)
        self._crosshair_overlay = CrosshairOverlay(self)
        self._crosshair_overlay.show()

        # Zoom history stack
        self._zoom_stack: list[QRectF] = []
        self._zoom_index: int = -1
        self._saving_zoom = True

        # Save initial viewport as zoom baseline (deferred until viewport is ready)
        self._needs_initial_save = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._crosshair_overlay.setGeometry(self.viewport().rect())

    def wheelEvent(self, event: QWheelEvent):
        # Disable scroll zoom — use ZOOM commands instead
        event.ignore()

    def mousePressEvent(self, event: QMouseEvent):
        if self.tool_manager and self.tool_manager._active_tool:
            if event.button() == Qt.MouseButton.LeftButton:
                scene_pos = self.mapToScene(event.pos())
                try:
                    self.tool_manager._active_tool.mouse_press(event, scene_pos)
                except Exception as e:
                    import traceback
                    print(f"MOUSE PRESS ERROR: {e}")
                    traceback.print_exc()
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton:
                # Right-click = Enter / Repeat last command (ACAD style)
                w = self.window()
                if hasattr(w, '_cmd_input'):
                    last_cmd = w._cmd_history[-1] if w._cmd_history else ""
                    if last_cmd:
                        w._cmd_input.setPlainText(last_cmd)
                        w._process_command(last_cmd)
                event.accept()
                return
        if event.button() == Qt.MouseButton.RightButton:
            # Repeat last command even with no active tool
            w = self.window()
            if hasattr(w, '_cmd_history') and w._cmd_history:
                last_cmd = w._cmd_history[-1]
                w._process_command(last_cmd)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        self._cursor_scene_pos = scene_pos
        self._crosshair_overlay.update()
        if self.tool_manager and self.tool_manager._active_tool:
            self.tool_manager._active_tool.mouse_move(event, scene_pos)
            if hasattr(self, '_status_callback') and self._status_callback:
                self._status_callback(scene_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
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
        if event.key() == Qt.Key.Key_F2:
            if hasattr(w, '_toggle_text_screen'):
                w._toggle_text_screen()
                event.accept()
                return
        if event.key() == Qt.Key.Key_F7:
            if hasattr(w, '_grid'):
                w._grid.setVisible(not w._grid.isVisible())
                event.accept()
                return
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

        # ESC → cancel tool + focus command line
        if event.key() == Qt.Key.Key_Escape:
            # Cancel active tool
            if hasattr(w, '_activate_tool'):
                w._activate_tool("select")
            # Jump to command line with blinking cursor
            if hasattr(w, '_cmd_input'):
                w._cmd_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                w._cmd_input.raise_()
                w._cmd_input.setFocus()
                w._cmd_input.setPlaceholderText("")
                w._cmd_input.setCursorWidth(3)
                # Also try focusing the parent dock
                p = w._cmd_input.parent()
                while p:
                    if hasattr(p, 'setFocus'):
                        p.setFocus()
                    p = p.parent()
            event.accept()
            return

        # Tool-switching shortcuts (like AutoCAD)
        key_map = {
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

        # Forward typing to command line (like ACAD)
        text = event.text()
        if text and text.isprintable():
            if hasattr(w, '_cmd_input'):
                w._cmd_input.setFocus()
                w._cmd_input.insertPlainText(text)
                w._cmd_input.ensureCursorVisible()
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
        if vr is None or vr.width() == 0 or vr.height() == 0:
            return
        current = QRectF(
            self.mapToScene(vr.rect()).boundingRect()
        )
        self._needs_initial_save = False
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
        if self._needs_initial_save:
            self._save_viewport()
        if self._zoom_index <= 0:
            return
        self._zoom_index -= 1
        rect = self._zoom_stack[self._zoom_index]
        self._saving_zoom = False
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._saving_zoom = True
