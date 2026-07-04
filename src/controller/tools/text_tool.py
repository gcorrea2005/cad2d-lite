from src.controller.tools.base_tool import BaseTool
from src.model.entities.text import TextEntity
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog


class TextTool(BaseTool):
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager

    def cursor(self):
        return QCursor(Qt.CursorShape.IBeamCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = Point(scene_pos.x(), scene_pos.y())
        text, ok = QInputDialog.getText(
            self.view, "Text", "Enter text:",
        )
        if ok and text.strip():
            entity = TextEntity(
                text = TextEntity(pt, content,
                                         layer_name=self._current_layer, color=self._current_color,
                                         linetype=self._current_linetype)
            )
            self.document.add_entity(entity)
            gfx = GfxTextItem(entity)
            self.view.scene().addItem(gfx)
