from src.controller.tools.base_tool import BaseTool
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class ExplodeTool(BaseTool):
    """Explode polyline into separate Line entities."""
    def cursor(self):
        return QCursor(Qt.CursorShape.PointingHandCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Polyline):
                self._explode_polyline(ent)
                self.view.scene().removeItem(item)
                break

    def _explode_polyline(self, pl: Polyline):
        segments = pl.segments()
        self.document.remove_entity(pl.uuid)
        for a, b in segments:
            # Skip zero-length segments
            if a.distance_to(b) < 0.0001:
                continue
            line = Line(a, b, layer_name=pl.layer_name, color=pl.color)
            self.document.add_entity(line)
