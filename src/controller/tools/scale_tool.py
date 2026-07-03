from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


class ScaleTool(BaseTool):
    """Scale selected entities around a base point by a factor."""
    def __init__(self, view, document):
        super().__init__(view, document)
        self._base: Point | None = None

    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        if self._base is None:
            self._base = pt
        else:
            # Ask for scale factor
            factor, ok = QInputDialog.getDouble(
                self.view, "Scale", "Scale factor:",
                1.0, -1000, 1000, 4)
            if ok and abs(factor) > 0.0001:
                self._scale_selected(factor)
            self._base = None

    def _scale_selected(self, factor: float):
        if self._base is None:
            return
        uuids = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
        if not uuids:
            uuids = [e.uuid for e in self.document.entities]

        for uuid in uuids:
            ent = self.document._entities.get(uuid)
            if ent is None:
                continue
            old_dict = ent.to_dict()

            def scale_pt(p: Point) -> Point:
                return Point(
                    self._base.x + (p.x - self._base.x) * factor,
                    self._base.y + (p.y - self._base.y) * factor,
                )

            if hasattr(ent, 'start') and hasattr(ent, 'end'):
                ent.start = scale_pt(ent.start)
                ent.end = scale_pt(ent.end)
            elif hasattr(ent, 'center'):
                ent.center = scale_pt(ent.center)
            elif hasattr(ent, 'position'):
                ent.position = scale_pt(ent.position)
            elif hasattr(ent, 'vertices'):
                ent.vertices = [scale_pt(v) for v in ent.vertices]
            elif hasattr(ent, 'def_point1'):
                ent.def_point1 = scale_pt(ent.def_point1)
                ent.def_point2 = scale_pt(ent.def_point2)
                ent.text_position = scale_pt(ent.text_position)

            self.document.execute(ModifyEntityCommand(ent, old_dict, ent.to_dict()))

    def deactivate(self):
        self._base = None
        super().deactivate()
