from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class RotateTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._selected: list[str] = []
        self._pivot: Point | None = None
        self._ref_angle: float = 0.0

    def activate(self):
        self._selected = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = Point(scene_pos.x(), scene_pos.y())
        if self._pivot is None:
            self._pivot = pt
        else:
            self._ref_angle = math.atan2(pt.y - self._pivot.y, pt.x - self._pivot.x)

    def mouse_release(self, event, scene_pos: QPointF):
        if self._pivot is None:
            return
        pt = Point(scene_pos.x(), scene_pos.y())
        new_angle = math.atan2(pt.y - self._pivot.y, pt.x - self._pivot.x)
        delta = new_angle - self._ref_angle

        if abs(delta) < 0.001:
            return

        cos_d = math.cos(delta)
        sin_d = math.sin(delta)

        for uuid in self._selected:
            ent = self.document._entities.get(uuid)
            if ent is None:
                continue
            old_dict = ent.to_dict()

            def rotate_pt(p: Point) -> Point:
                dx = p.x - self._pivot.x
                dy = p.y - self._pivot.y
                return Point(
                    self._pivot.x + dx * cos_d - dy * sin_d,
                    self._pivot.y + dx * sin_d + dy * cos_d,
                )

            if hasattr(ent, 'start') and hasattr(ent, 'end'):
                ent.start = rotate_pt(ent.start)
                ent.end = rotate_pt(ent.end)
            elif hasattr(ent, 'center'):
                ent.center = rotate_pt(ent.center)
            elif hasattr(ent, 'position'):
                ent.position = rotate_pt(ent.position)
            elif hasattr(ent, 'vertices'):
                ent.vertices = [rotate_pt(v) for v in ent.vertices]
            elif hasattr(ent, 'def_point1'):
                ent.def_point1 = rotate_pt(ent.def_point1)
                ent.def_point2 = rotate_pt(ent.def_point2)
                ent.text_position = rotate_pt(ent.text_position)

            self.document.execute(ModifyEntityCommand(ent, old_dict, ent.to_dict()))
