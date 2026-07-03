from src.controller.tools.base_tool import BaseTool
from src.model.entities.arc import Arc
from src.model.entities.base import Point
from src.view.graphics.entity_items import GfxArcItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class ArcTool(BaseTool):
    """3-point arc: center, start, end."""
    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._center: Point | None = None
        self._start: Point | None = None
        self._preview_item: GfxArcItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = Point(scene_pos.x(), scene_pos.y())
        if self._center is None:
            self._center = pt
        elif self._start is None:
            self._start = pt
        else:
            # Create arc from center, start, end
            radius = self._center.distance_to(self._start)
            start_angle = math.atan2(self._start.y - self._center.y,
                                     self._start.x - self._center.x)
            end_angle = math.atan2(pt.y - self._center.y,
                                   pt.x - self._center.x)
            # Normalize to positive angles
            if start_angle < 0:
                start_angle += 2 * math.pi
            if end_angle < 0:
                end_angle += 2 * math.pi
            if end_angle <= start_angle:
                end_angle += 2 * math.pi

            arc = Arc(self._center, radius, start_angle, end_angle,
                      layer_name=self.layer_manager.current_layer_name)
            self.document.add_entity(arc)
            gfx = GfxArcItem(arc)
            self.view.scene().addItem(gfx)
            self._center = None
            self._start = None
            self._clear_preview()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._center is not None:
            self._clear_preview()
            pt = Point(scene_pos.x(), scene_pos.y())
            if self._start is None:
                # Preview radius from center
                radius = self._center.distance_to(pt)
                preview = Arc(self._center, radius, 0, math.pi * 1.5, color="#888888")
                self._preview_item = GfxArcItem(preview)
            else:
                # Preview actual arc
                radius = self._center.distance_to(self._start)
                start_angle = math.atan2(self._start.y - self._center.y,
                                         self._start.x - self._center.x)
                end_angle = math.atan2(pt.y - self._center.y,
                                       pt.x - self._center.x)
                if start_angle < 0:
                    start_angle += 2 * math.pi
                if end_angle < 0:
                    end_angle += 2 * math.pi
                if end_angle <= start_angle:
                    end_angle += 2 * math.pi
                preview = Arc(self._center, radius, start_angle, end_angle, color="#888888")
                self._preview_item = GfxArcItem(preview)
            self.view.scene().addItem(self._preview_item)

    def _clear_preview(self):
        if self._preview_item:
            self.view.scene().removeItem(self._preview_item)
            self._preview_item = None

    def deactivate(self):
        self._clear_preview()
        self._center = None
        self._start = None
