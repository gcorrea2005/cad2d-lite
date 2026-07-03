from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor, QPen, QColor
from PySide6.QtWidgets import QGraphicsLineItem
import math


class MirrorTool(BaseTool):
    """Mirror selected entities across a line defined by 2 clicks."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._p1: Point | None = None
        self._p2: Point | None = None
        self._axis_line: QGraphicsLineItem | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._p1 is None:
            self._p1 = pt
        elif self._p2 is None:
            self._p2 = pt
            # Show axis line briefly then execute mirror
            self._mirror_selected()
            self._p1 = None
            self._p2 = None
            self._clear_axis()

    def mouse_move(self, event, scene_pos: QPointF):
        if self._p1 is not None:
            self._clear_axis()
            pt = self._snap(scene_pos)
            from PySide6.QtCore import QLineF
            self._axis_line = QGraphicsLineItem(
                QLineF(QPointF(self._p1.x, self._p1.y),
                       QPointF(pt.x, pt.y)))
            pen = QPen(QColor("#FFCC00"))
            pen.setStyle(Qt.PenStyle.DashLine)
            self._axis_line.setPen(pen)
            self._axis_line.setZValue(10000)
            self.view.scene().addItem(self._axis_line)

    def _mirror_selected(self):
        if self._p1 is None or self._p2 is None:
            return
        # Mirror axis: line p1 -> p2
        dx = self._p2.x - self._p1.x
        dy = self._p2.y - self._p1.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return

        uuids = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
        if not uuids:
            # Mirror all entities if nothing selected
            uuids = [e.uuid for e in self.document.entities]

        for uuid in uuids:
            ent = self.document._entities.get(uuid)
            if ent is None:
                continue
            old_dict = ent.to_dict()

            def mirror_pt(p: Point) -> Point:
                # Project point onto line, reflect
                t = ((p.x - self._p1.x) * dx + (p.y - self._p1.y) * dy) / length_sq
                proj_x = self._p1.x + t * dx
                proj_y = self._p1.y + t * dy
                return Point(2 * proj_x - p.x, 2 * proj_y - p.y)

            if hasattr(ent, 'start') and hasattr(ent, 'end'):
                ent.start = mirror_pt(ent.start)
                ent.end = mirror_pt(ent.end)
            elif hasattr(ent, 'center'):
                ent.center = mirror_pt(ent.center)
            elif hasattr(ent, 'position'):
                ent.position = mirror_pt(ent.position)
            elif hasattr(ent, 'vertices'):
                ent.vertices = [mirror_pt(v) for v in ent.vertices]
            elif hasattr(ent, 'def_point1'):
                ent.def_point1 = mirror_pt(ent.def_point1)
                ent.def_point2 = mirror_pt(ent.def_point2)
                ent.text_position = mirror_pt(ent.text_position)

            self.document.execute(ModifyEntityCommand(ent, old_dict, ent.to_dict()))

    def _clear_axis(self):
        if self._axis_line:
            self.view.scene().removeItem(self._axis_line)
            self._axis_line = None

    def deactivate(self):
        self._clear_axis()
        self._p1 = None
        self._p2 = None
        super().deactivate()
