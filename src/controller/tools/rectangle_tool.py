from src.controller.tools.base_tool import BaseTool
from src.model.entities.polyline import Polyline
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxPolylineItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class RectangleTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._corner1: Point | None = None
        self._preview_item: GfxPolylineItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._corner1 is None:
            self._corner1 = pt
        else:
            x1, y1 = self._corner1.x, self._corner1.y
            x2, y2 = pt.x, pt.y
            rect = Polyline(
                [Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)],
                closed=True,
                layer_name=self._current_layer, color=self._current_color,
                linetype=self._current_linetype,
            )
            self.document.add_entity(rect)
            gfx = GfxPolylineItem(rect)
            self.view.scene().addItem(gfx)
            self._corner1 = None
            self._clear_preview()
            self._clear_snap_indicator()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._corner1 is not None:
            self._clear_preview()
            pt = self._snap(scene_pos)
            x1, y1 = self._corner1.x, self._corner1.y
            x2, y2 = pt.x, pt.y
            preview = Polyline(
                [Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)],
                closed=True, color="#888888",
            )
            self._preview_item = GfxPolylineItem(preview)
            self.view.scene().addItem(self._preview_item)

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def deactivate(self):
        self._clear_preview()
        self._corner1 = None
        super().deactivate()
