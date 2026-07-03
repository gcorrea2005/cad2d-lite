from src.controller.tools.base_tool import BaseTool
from src.model.entities.polyline import Polyline
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxPolylineItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class PolylineTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._points: list[Point] = []
        self._preview_item: GfxPolylineItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if event.button() == Qt.MouseButton.RightButton:
            if len(self._points) >= 2:
                pl = Polyline(self._points.copy(), closed=False,
                              layer_name=self.layer_manager.current_layer_name)
                self.document.add_entity(pl)
                gfx = GfxPolylineItem(pl)
                self.view.scene().addItem(gfx)
            self._reset()
        else:
            self._points.append(pt)

    def mouse_move(self, event, scene_pos: QPointF):
        if len(self._points) >= 1:
            self._clear_preview()
            pt = self._snap(scene_pos)
            preview_pts = self._points + [pt]
            preview = Polyline(preview_pts, color="#888888")
            self._preview_item = GfxPolylineItem(preview)
            self.view.scene().addItem(self._preview_item)

    def key_press(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._reset()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if len(self._points) >= 2:
                pl = Polyline(self._points.copy(), closed=False,
                              layer_name=self.layer_manager.current_layer_name)
                self.document.add_entity(pl)
                gfx = GfxPolylineItem(pl)
                self.view.scene().addItem(gfx)
            self._reset()

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def _reset(self):
        self._clear_preview()
        self._points = []
        self._clear_snap_indicator()

    def deactivate(self):
        self._reset()
        super().deactivate()
