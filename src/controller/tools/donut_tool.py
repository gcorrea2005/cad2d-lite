"""DONUT tool — filled ring (two concentric circles)."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.circle import Circle
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxCircleItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog


class DonutTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._center: Point | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)

        if self._center is None:
            self._center = pt
        else:
            # Inner radius = distance to center, outer = inner + thickness
            inner_r = self._center.distance_to(pt)
            outer_r, ok = QInputDialog.getDouble(
                self.view, "Donut", "Outer radius:", inner_r + 0.5, inner_r + 0.1, 100, 2)
            if not ok:
                self._center = None
                return

            inner = Circle(self._center, inner_r,
                           layer_name=self._current_layer, color=self._current_color)
            outer = Circle(self._center, outer_r,
                           layer_name=self._current_layer, color=self._current_color)
            self.document.add_entity(inner)
            self.document.add_entity(outer)
            self.view.scene().addItem(GfxCircleItem(inner))
            self.view.scene().addItem(GfxCircleItem(outer))
            self._center = None

    def deactivate(self):
        self._center = None
        super().deactivate()
