from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.polyline import Polyline
from src.view.graphics.entity_items import GfxPolylineItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor, QColor, QPen
from PySide6.QtWidgets import QInputDialog, QColorDialog


class SolidTool(BaseTool):
    """Draw filled polygon (closed polyline with fill color)."""
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._points: list[Point] = []
        self._fill_color: str = "#884444"

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if event.button() == Qt.MouseButton.RightButton:
            if len(self._points) >= 3:
                color = QColorDialog.getColor(QColor(self._fill_color),
                                              self.view, "Solid Fill Color")
                if color.isValid():
                    self._fill_color = color.name()
                self._create_solid()
            self._points = []
            return
        self._points.append(pt)

    def key_press(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if len(self._points) >= 3:
                self._create_solid()
            self._points = []
        elif event.key() == Qt.Key.Key_Escape:
            self._points = []

    def _create_solid(self):
        pl = Polyline(self._points.copy(), closed=True,
                      color=self._fill_color,
                      layer_name=self.layer_manager.current_layer_name)
        self.document.add_entity(pl)
        # Override the graphics item to show fill
        # We reuse GfxPolylineItem but we can't easily fill it without custom paint
        # So we just draw the outline for now — the fill color is stored
        gfx = GfxPolylineItem(pl)
        self.view.scene().addItem(gfx)

    def deactivate(self):
        self._points = []
        super().deactivate()
