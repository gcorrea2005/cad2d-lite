from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.point_entity import PointEntity
from src.view.graphics.entity_items import GfxPointItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class PointTool(BaseTool):
    """Place point entities."""
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        entity = PointEntity(pt, layer_name=self.layer_manager.current_layer_name)
        entity._document = self.document  # for PDMODE/PDSIZE access
        self.document.add_entity(entity)
        gfx = GfxPointItem(entity)
        self.view.scene().addItem(gfx)
