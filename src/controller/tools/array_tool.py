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
from PySide6.QtWidgets import QInputDialog


class ArrayTool(BaseTool):
    """Rectangular array: duplicate selection in rows x cols grid."""
    def cursor(self):
        return QCursor(Qt.CursorShape.CrossCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        rows, ok = QInputDialog.getInt(self.view, "Array", "Rows:", 2, 1, 100)
        if not ok:
            return
        cols, ok = QInputDialog.getInt(self.view, "Array", "Columns:", 2, 1, 100)
        if not ok:
            return
        spacing_x, ok = QInputDialog.getDouble(
            self.view, "Array", "Column spacing:", 10.0, 0.001, 100000, 4)
        if not ok:
            return
        spacing_y, ok = QInputDialog.getDouble(
            self.view, "Array", "Row spacing:", 10.0, 0.001, 100000, 4)
        if not ok:
            return

        uuids = list(self.view._selected_uuids) if hasattr(self.view, '_selected_uuids') else []
        if not uuids:
            uuids = [e.uuid for e in self.document.entities]

        for row in range(rows):
            for col in range(cols):
                if row == 0 and col == 0:
                    continue  # skip original position
                dx = col * spacing_x
                dy = row * spacing_y
                for uuid in uuids:
                    ent = self.document._entities.get(uuid)
                    if ent is None:
                        continue
                    data = ent.to_dict()
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
