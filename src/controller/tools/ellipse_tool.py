"""Ellipse tool — center + major axis + ratio."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.ellipse import Ellipse
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxEllipseItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class EllipseTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._center: Point | None = None
        self._major_pt: Point | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._center is None:
            self._center = pt
        elif self._major_pt is None:
            self._major_pt = pt
        else:
            # Calculate ratio from distance
            r_maj = self._center.distance_to(self._major_pt)
            r_min = self._center.distance_to(pt)
            ratio = min(r_min / r_maj, 1.0) if r_maj > 0 else 1.0

            ellipse = Ellipse(self._center, self._major_pt, ratio,
                              layer_name=self._current_layer,
                              color=self._current_color,
                              linetype=self._current_linetype)
            self.document.add_entity(ellipse)
            self.view.scene().addItem(GfxEllipseItem(ellipse))
            self._center = None
            self._major_pt = None

    def deactivate(self):
        self._center = None
        self._major_pt = None
        super().deactivate()
