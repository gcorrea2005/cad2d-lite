from src.controller.tools.base_tool import BaseTool
from src.model.entities.dimension import Dimension
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxDimensionItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class DimLinearTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._p1: Point | None = None
        self._p2: Point | None = None
        self._preview_item: GfxDimensionItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._p1 is None:
            self._p1 = pt
        elif self._p2 is None:
            self._p2 = pt
        else:
            dim = Dimension(self._p1, self._p2, pt,
                            layer_name=self.layer_manager.current_layer_name)
            self.document.add_entity(dim)
            gfx = GfxDimensionItem(dim)
            self.view.scene().addItem(gfx)
            self._p1 = None
            self._p2 = None
            self._clear_preview()
            self._clear_snap_indicator()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._p1 is not None and self._p2 is not None:
            self._clear_preview()
            pt = self._snap(scene_pos)
            preview = Dimension(self._p1, self._p2, pt, color="#888888")
            self._preview_item = GfxDimensionItem(preview)
            self.view.scene().addItem(self._preview_item)

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def deactivate(self):
        self._clear_preview()
        self._p1 = None
        self._p2 = None
        super().deactivate()
