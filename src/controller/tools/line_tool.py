from src.controller.tools.base_tool import BaseTool
from src.model.entities.line import Line
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxLineItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class LineTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._first_point: Point | None = None
        self._preview_item: GfxLineItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos, self._first_point)
        self._clear_transient_snap()  # consumed after this pick
        if self._first_point is None:
            self._first_point = pt
        else:
            line = Line(self._first_point, pt,
                        layer_name=self._current_layer,
                        color=self._current_color,
                        linetype=self._current_linetype)
            self.document.add_entity(line)
            gfx = GfxLineItem(line)
            self.view.scene().addItem(gfx)
            self._first_point = None
            self._clear_preview()
            self._clear_snap_indicator()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._first_point is not None:
            self._clear_preview()
            pt = self._snap(scene_pos, self._first_point)
            preview_entity = Line(self._first_point, pt, color="#888888")
            self._preview_item = GfxLineItem(preview_entity)
            self.view.scene().addItem(self._preview_item)

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def deactivate(self):
        self._clear_preview()
        self._first_point = None
        super().deactivate()
