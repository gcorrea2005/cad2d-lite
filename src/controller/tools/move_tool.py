from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.controller.commands.modify_entity import ModifyEntityCommand
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class MoveTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._selected: list[str] = []
        self._base_point: Point | None = None
        self._start_positions: dict[str, Point] = {}

    def activate(self):
        self._selected = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
        if not self._selected:
            self._selected = [e.uuid for e in self.document.entities]

    def cursor(self):
        return QCursor(Qt.CursorShape.SizeAllCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        self._base_point = Point(scene_pos.x(), scene_pos.y())
        self._start_positions = {}
        for uuid in self._selected:
            ent = self.document._entities.get(uuid)
            if ent and hasattr(ent, 'start'):
                # Store the reference point (start for line-like, center for circles)
                if hasattr(ent, 'center'):
                    self._start_positions[uuid] = ent.center
                elif hasattr(ent, 'start'):
                    self._start_positions[uuid] = ent.start
                elif hasattr(ent, 'position'):
                    self._start_positions[uuid] = ent.position

    def mouse_move(self, event, scene_pos: QPointF):
        pass  # Preview handled on release for simplicity

    def mouse_release(self, event, scene_pos: QPointF):
        if self._base_point is None:
            return
        new_pt = Point(scene_pos.x(), scene_pos.y())
        dx = new_pt.x - self._base_point.x
        dy = new_pt.y - self._base_point.y

        for uuid in self._selected:
            ent = self.document._entities.get(uuid)
            if ent is None:
                continue
            old_dict = ent.to_dict()

            if hasattr(ent, 'start') and hasattr(ent, 'end'):
                ent.start = Point(ent.start.x + dx, ent.start.y + dy)
                ent.end = Point(ent.end.x + dx, ent.end.y + dy)
            elif hasattr(ent, 'center'):
                ent.center = Point(ent.center.x + dx, ent.center.y + dy)
            elif hasattr(ent, 'position'):
                ent.position = Point(ent.position.x + dx, ent.position.y + dy)
            elif hasattr(ent, 'vertices'):
                ent.vertices = [Point(v.x + dx, v.y + dy) for v in ent.vertices]
            elif hasattr(ent, 'def_point1'):
                ent.def_point1 = Point(ent.def_point1.x + dx, ent.def_point1.y + dy)
                ent.def_point2 = Point(ent.def_point2.x + dx, ent.def_point2.y + dy)
                ent.text_position = Point(ent.text_position.x + dx, ent.text_position.y + dy)

            self.document.execute(ModifyEntityCommand(ent, old_dict, ent.to_dict()))

        self._base_point = None
