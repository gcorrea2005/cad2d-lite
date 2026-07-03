from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem


class SelectTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._start_point: QPointF | None = None
        self._rubber_band: QGraphicsRectItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.ArrowCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Check if clicking on an entity (single click select)
        items = self.view.scene().items(scene_pos)
        entity_items = [it for it in items if hasattr(it, 'entity')]

        if entity_items:
            # Select single entity
            self._clear_selection()
            item = entity_items[0]
            self._highlight_item(item, True)
            self.view._selected_uuids = [item.entity.uuid]
        else:
            self._clear_selection()
            self.view._selected_uuids = []
            # Start rubber band for window selection
            self._start_point = scene_pos
            self._rubber_band = QGraphicsRectItem()
            pen = QPen(QColor("#00AAFF"))
            pen.setStyle(Qt.PenStyle.DashLine)
            self._rubber_band.setPen(pen)
            self._rubber_band.setZValue(1000)
            self.view.scene().addItem(self._rubber_band)

    def mouse_move(self, event, scene_pos: QPointF):
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self._rubber_band.setRect(rect)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None

            # Window selection
            self._clear_selection()
            selected = []
            for item in self.view.scene().items(rect):
                if hasattr(item, 'entity') and hasattr(item.entity, 'uuid'):
                    self._highlight_item(item, True)
                    selected.append(item.entity.uuid)
            self.view._selected_uuids = selected

        self._start_point = None

    def _highlight_item(self, item, selected: bool):
        """Toggle visual selection highlighting."""
        if selected:
            item.setSelected(True)
        else:
            item.setSelected(False)

    def _clear_selection(self):
        """Deselect all entities."""
        for item in list(self.view.scene().items()):
            if hasattr(item, 'entity'):
                item.setSelected(False)
        if hasattr(self.view, '_selected_uuids'):
            self.view._selected_uuids = []

    def key_press(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            uuids = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
            for uuid in uuids:
                if uuid in self.document._entities:
                    self.document.remove_entity(uuid)
            # Remove graphics
            for item in list(self.view.scene().items()):
                if hasattr(item, 'entity') and item.entity.uuid in uuids:
                    self.view.scene().removeItem(item)
            self.view._selected_uuids = []

    def deactivate(self):
        if self._rubber_band:
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
        self._start_point = None
