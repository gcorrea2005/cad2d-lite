from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class DeleteTool(BaseTool):
    """Quick delete: click entity to remove it. Also works via delete key in CadView."""
    def __init__(self, view, document):
        super().__init__(view, document)

    def cursor(self):
        return QCursor(Qt.CursorShape.PointingHandCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Find entity under cursor and delete it
        items = self.view.scene().items(scene_pos)
        for item in items:
            if hasattr(item, 'entity') and hasattr(item.entity, 'uuid'):
                uuid = item.entity.uuid
                if uuid in self.document._entities:
                    self.document.remove_entity(uuid)
                    self.view.scene().removeItem(item)
                    break
