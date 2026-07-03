from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
import math


class CopyTool(BaseTool):
    def __init__(self, view, document):
        super().__init__(view, document)
        self._selected: list[str] = []
        self._base_point: Point | None = None

    def activate(self):
        self._selected = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
        if not self._selected:
            self._selected = [e.uuid for e in self.document.entities]

    def cursor(self):
        return QCursor(Qt.CursorShape.DragCopyCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        self._base_point = Point(scene_pos.x(), scene_pos.y())

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
            data = ent.to_dict()
            # Remove uuid so clone gets a new one
            data.pop("uuid", None)

            if data["type"] == "Line":
                data["start"] = [data["start"][0] + dx, data["start"][1] + dy]
                data["end"] = [data["end"][0] + dx, data["end"][1] + dy]
                clone = Line.from_dict(data)
            elif data["type"] == "Circle":
                data["center"] = [data["center"][0] + dx, data["center"][1] + dy]
                clone = Circle.from_dict(data)
            elif data["type"] == "Arc":
                data["center"] = [data["center"][0] + dx, data["center"][1] + dy]
                clone = Arc.from_dict(data)
            elif data["type"] == "Polyline":
                data["vertices"] = [[v[0] + dx, v[1] + dy] for v in data["vertices"]]
                clone = Polyline.from_dict(data)
            elif data["type"] == "Text":
                data["position"] = [data["position"][0] + dx, data["position"][1] + dy]
                clone = TextEntity.from_dict(data)
            elif data["type"] == "Dimension":
                data["def_point1"] = [data["def_point1"][0] + dx, data["def_point1"][1] + dy]
                data["def_point2"] = [data["def_point2"][0] + dx, data["def_point2"][1] + dy]
                data["text_position"] = [data["text_position"][0] + dx, data["text_position"][1] + dy]
                clone = Dimension.from_dict(data)
            else:
                continue

            self.document.add_entity(clone)

        self._base_point = None
