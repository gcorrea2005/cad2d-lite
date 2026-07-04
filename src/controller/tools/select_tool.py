from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from src.model.entities.base import Point


class SelectTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._start_point: QPointF | None = None
        self._rubber_band: QGraphicsRectItem | None = None
        self._grips: list[QGraphicsRectItem] = []
        self._dragging_grip: int | None = None
        self._grip_points: list[Point] = []
        self._grip_entity = None

    def cursor(self):
        return QCursor(Qt.CursorShape.ArrowCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Check if clicking on a grip
        if self._grips:
            for i, grip in enumerate(self._grips):
                if grip.contains(self.view.mapFromScene(scene_pos)):
                    self._dragging_grip = i
                    return
            # Click outside grips = deselect
            self._clear_grips()

        # Check if clicking on an entity
        items = self.view.scene().items(scene_pos)
        entity_items = [it for it in items if hasattr(it, 'entity')]

        if entity_items:
            self._clear_selection()
            item = entity_items[0]
            self._highlight_item(item, True)
            self.view._selected_uuids = [item.entity.uuid]
            self._show_grips(item)
        else:
            self._clear_selection()
            self.view._selected_uuids = []
            self._clear_grips()
            # Start rubber band
            self._start_point = scene_pos
            self._rubber_band = QGraphicsRectItem()
            pen = QPen(QColor("#00AAFF"))
            pen.setStyle(Qt.PenStyle.DashLine)
            self._rubber_band.setPen(pen)
            self._rubber_band.setZValue(1000)
            self.view.scene().addItem(self._rubber_band)

    def mouse_move(self, event, scene_pos: QPointF):
        if self._dragging_grip is not None and self._grip_entity and self._grip_points:
            # Stretch: move the grip point
            ent = self._grip_entity
            gp = self._grip_points
            idx = self._dragging_grip
            pt = self._snap(scene_pos)

            # Update entity based on type
            from src.model.entities.line import Line
            from src.model.entities.circle import Circle
            import math

            if isinstance(ent, Line):
                if idx == 0:  # start
                    ent.start = pt
                elif idx == 1:  # end
                    ent.end = pt
                elif idx == 2:  # midpoint — move whole line
                    dx = pt.x - gp[2].x
                    dy = pt.y - gp[2].y
                    ent.start = Point(ent.start.x + dx, ent.start.y + dy)
                    ent.end = Point(ent.end.x + dx, ent.end.y + dy)
            elif isinstance(ent, Circle):
                if idx == 0:
                    ent.center = pt
                else:
                    ent.radius = ent.center.distance_to(pt)
            # Update grips
            self._clear_grips()
            gfx = self._find_gfx(ent)
            if gfx:
                self._show_grips(gfx)
            return

        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self._rubber_band.setRect(rect)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._dragging_grip is not None:
            self._dragging_grip = None
            return
        if self._rubber_band and self._start_point:
            rect = QRectF(self._start_point, scene_pos).normalized()
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
            self._clear_selection()
            selected = []
            for item in self.view.scene().items(rect):
                if hasattr(item, 'entity') and hasattr(item.entity, 'uuid'):
                    self._highlight_item(item, True)
                    selected.append(item.entity.uuid)
            self.view._selected_uuids = selected
        self._start_point = None

    def _show_grips(self, item):
        """Create grip squares at entity key points."""
        self._clear_grips()
        ent = item.entity
        self._grip_entity = ent
        self._grip_points = []

        from src.model.entities.line import Line
        from src.model.entities.circle import Circle
        from src.model.entities.arc import Arc
        import math

        size = 4
        if isinstance(ent, Line):
            pts = [Point(ent.start.x, ent.start.y),
                   Point(ent.end.x, ent.end.y),
                   Point((ent.start.x + ent.end.x) / 2, (ent.start.y + ent.end.y) / 2)]
        elif isinstance(ent, Circle):
            pts = [Point(ent.center.x, ent.center.y)]
            r = ent.radius
            for a in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                pts.append(Point(ent.center.x + r * math.cos(a), ent.center.y + r * math.sin(a)))
        else:
            return  # unsupported

        self._grip_points = pts
        for p in pts:
            grip = QGraphicsRectItem(QRectF(p.x - size, p.y - size, size * 2, size * 2))
            grip.setPen(QPen(QColor("#0000FF"), 1))
            grip.setBrush(QBrush(QColor("#4488FF")))
            grip.setZValue(2000)
            self.view.scene().addItem(grip)
            self._grips.append(grip)

    def _find_gfx(self, ent):
        """Find the GfxItem for an entity."""
        for item in self.view.scene().items():
            if hasattr(item, 'entity') and item.entity is ent:
                return item
        return None

    def _clear_grips(self):
        for g in self._grips:
            self.view.scene().removeItem(g)
        self._grips = []
        self._grip_points = []
        self._grip_entity = None
        self._dragging_grip = None

    def _highlight_item(self, item, selected: bool):
        if selected:
            item.setSelected(True)
        else:
            item.setSelected(False)

    def _clear_selection(self):
        self._clear_grips()
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
            for item in list(self.view.scene().items()):
                if hasattr(item, 'entity') and item.entity.uuid in uuids:
                    self.view.scene().removeItem(item)
            self.view._selected_uuids = []
            self._clear_grips()

    def deactivate(self):
        if self._rubber_band:
            self.view.scene().removeItem(self._rubber_band)
            self._rubber_band = None
        self._start_point = None
        self._clear_grips()
