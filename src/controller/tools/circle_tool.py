from src.controller.tools.base_tool import BaseTool
from src.model.entities.circle import Circle
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxCircleItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class CircleTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._center: Point | None = None
        self._preview_item: GfxCircleItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = Point(scene_pos.x(), scene_pos.y())
        if self._center is None:
            self._center = pt
        else:
            radius = self._center.distance_to(pt)
            circle = Circle(self._center, radius,
                            layer_name=self.layer_manager.current_layer_name)
            self.document.add_entity(circle)
            gfx = GfxCircleItem(circle)
            self.view.scene().addItem(gfx)
            self._center = None
            self._clear_preview()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._center is not None:
            self._clear_preview()
            pt = Point(scene_pos.x(), scene_pos.y())
            radius = self._center.distance_to(pt)
            preview = Circle(self._center, radius, color="#888888")
            self._preview_item = GfxCircleItem(preview)
            self.view.scene().addItem(self._preview_item)

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def deactivate(self):
        self._clear_preview()
        self._center = None
