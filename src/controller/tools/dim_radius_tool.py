"""DIMRADIUS tool — dimension a circle or arc radius."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.dimension import Dimension
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxDimensionItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class DimRadiusTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._center: Point | None = None
        self._edge: Point | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._center is None:
            self._center = pt
        elif self._edge is None:
            self._edge = pt
        else:
            dim = Dimension(self._center, self._edge, pt, dim_type="radius",
                            layer_name=self._current_layer, color=self._current_color)
            self.document.add_entity(dim)
            gfx = GfxDimensionItem(dim)
            self.view.scene().addItem(gfx)
            self._center = None
            self._edge = None
            self._clear_snap_indicator()

    def deactivate(self):
        self._center = None
        self._edge = None
        super().deactivate()
