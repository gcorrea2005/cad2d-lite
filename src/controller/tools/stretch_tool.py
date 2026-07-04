"""STRETCH tool — move vertices inside a crossing window."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor
from PySide6.QtWidgets import QGraphicsRectItem


class StretchTool(BaseTool):
    """Crossing window → select vertices → stretch them."""

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def __init__(self, view, document, layer_manager):
        super().__init__(view, document)
        self.layer_manager = layer_manager
        self._corner1: Point | None = None
        self._corner2: Point | None = None
        self._base_point: Point | None = None
        self._rubber: QGraphicsRectItem | None = None
        self._affected: list[tuple] = []  # (entity, vertex_index_or_attr)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)

        if self._corner1 is None:
            self._corner1 = pt
            self._rubber = QGraphicsRectItem()
            pen = QPen(QColor("#00FF44"))
            pen.setStyle(Qt.PenStyle.DashLine)
            self._rubber.setPen(pen)
            self._rubber.setZValue(1000)
            self.view.scene().addItem(self._rubber)
        elif self._corner2 is None:
            self._corner2 = pt
            if self._rubber:
                self.view.scene().removeItem(self._rubber)
                self._rubber = None
            # Select vertices in crossing window
            self._select_vertices()
            if not self._affected:
                self._reset()
                return
        elif self._base_point is None:
            self._base_point = pt
        else:
            # Apply displacement
            dx = pt.x - self._base_point.x
            dy = pt.y - self._base_point.y
            self._apply_stretch(dx, dy)
            self._reset()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._rubber and self._corner1:
            p = self._snap(scene_pos)
            rect = QRectF(
                min(self._corner1.x, p.x), min(self._corner1.y, p.y),
                abs(p.x - self._corner1.x), abs(p.y - self._corner1.y),
            )
            self._rubber.setRect(rect)

    def _select_vertices(self):
        """Find all entity vertices inside the crossing rectangle."""
        x1 = min(self._corner1.x, self._corner2.x)
        x2 = max(self._corner1.x, self._corner2.x)
        y1 = min(self._corner1.y, self._corner2.y)
        y2 = max(self._corner1.y, self._corner2.y)

        self._affected = []

        for ent in self.document.entities:
            if isinstance(ent, Line):
                s_in = x1 <= ent.start.x <= x2 and y1 <= ent.start.y <= y2
                e_in = x1 <= ent.end.x <= x2 and y1 <= ent.end.y <= y2
                if s_in:
                    self._affected.append((ent, 'start'))
                if e_in:
                    self._affected.append((ent, 'end'))
            elif isinstance(ent, Circle):
                if x1 <= ent.center.x <= x2 and y1 <= ent.center.y <= y2:
                    self._affected.append((ent, 'center'))
            elif isinstance(ent, Polyline):
                for i, v in enumerate(ent.vertices):
                    if x1 <= v.x <= x2 and y1 <= v.y <= y2:
                        self._affected.append((ent, i))

    def _apply_stretch(self, dx: float, dy: float):
        """Move selected vertices by (dx, dy)."""
        seen = set()
        for ent, key in self._affected:
            eid = id(ent)
            if isinstance(ent, Line):
                if key == 'start':
                    ent.start = Point(ent.start.x + dx, ent.start.y + dy)
                elif key == 'end':
                    ent.end = Point(ent.end.x + dx, ent.end.y + dy)
            elif isinstance(ent, Circle):
                ent.center = Point(ent.center.x + dx, ent.center.y + dy)
            elif isinstance(ent, Polyline):
                v = ent.vertices[key]
                ent.vertices[key] = Point(v.x + dx, v.y + dy)
            seen.add(eid)

        # Update graphics
        from src.view.graphics.entity_items import (
            GfxLineItem, GfxCircleItem, GfxArcItem,
            GfxPolylineItem, GfxTextItem, GfxDimensionItem, GfxPointItem,
        )
        # Rebuild affected entities in scene
        for item in list(self.view.scene().items()):
            if hasattr(item, 'entity') and id(item.entity) in seen:
                self.view.scene().removeItem(item)

        for ent in self.document.entities:
            if id(ent) not in seen:
                continue
            if isinstance(ent, Line):
                self.view.scene().addItem(GfxLineItem(ent))
            elif isinstance(ent, Circle):
                self.view.scene().addItem(GfxCircleItem(ent))
            elif isinstance(ent, Arc):
                self.view.scene().addItem(GfxArcItem(ent))
            elif isinstance(ent, Polyline):
                self.view.scene().addItem(GfxPolylineItem(ent))

    def _reset(self):
        self._corner1 = None
        self._corner2 = None
        self._base_point = None
        self._affected = []
        if self._rubber:
            self.view.scene().removeItem(self._rubber)
            self._rubber = None

    def deactivate(self):
        self._reset()
        super().deactivate()
