"""DIMBASELINE tool — chain dimensions from a baseline."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.dimension import Dimension
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxDimensionItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class DimBaselineTool(BaseTool):
    """First dim = baseline, subsequent clicks add more dims from same origin."""

    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._baseline: Point | None = None
        self._p1: Point | None = None
        self._p2: Point | None = None
        self._offset_y: float | None = None
        self._first: bool = True

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)

        if self._first:
            # First: place the baseline dimension (like DIMLINEAR)
            if self._p1 is None:
                self._p1 = pt
            elif self._p2 is None:
                self._p2 = pt
            else:
                self._baseline = self._p1  # origin for baseline chain
                self._offset_y = pt.y  # dim line position
                dim = Dimension(self._p1, self._p2, pt, dim_type="linear",
                                layer_name=self._current_layer, color=self._current_color)
                self.document.add_entity(dim)
                self.view.scene().addItem(GfxDimensionItem(dim))
                self._first = False
                self._p1 = None
                self._p2 = None
        else:
            # Subsequent clicks: dim from baseline to this point
            dim = Dimension(self._baseline, pt, Point(self._baseline.x, self._offset_y),
                            dim_type="linear", layer_name=self._current_layer, color=self._current_color)
            self.document.add_entity(dim)
            self.view.scene().addItem(GfxDimensionItem(dim))
            self._offset_y += 15  # stack offset for next dim

    def deactivate(self):
        self._p1 = None
        self._p2 = None
        self._offset_y = None
        self._first = True
        super().deactivate()
