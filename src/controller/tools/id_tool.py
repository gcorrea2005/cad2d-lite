from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class IdTool(BaseTool):
    """ID inquiry: click entity or point to show properties."""
    def __init__(self, view, document, echo_fn):
        super().__init__(view, document)
        self._echo = echo_fn

    def cursor(self):
        return QCursor(Qt.CursorShape.WhatsThisCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        # Check if clicking on an entity
        items = self.view.scene().items(scene_pos)
        for item in items:
            if hasattr(item, 'entity') and hasattr(item.entity, 'uuid'):
                e = item.entity
                d = e.to_dict()
                self._echo(f"ID: {d['type']}  Layer={e.layer_name}")
                self._echo(f"     uuid={e.uuid}")
                if hasattr(e, 'start'):
                    self._echo(f"     Start: {e.start.x:.4f}, {e.start.y:.4f}")
                if hasattr(e, 'end'):
                    self._echo(f"     End:   {e.end.x:.4f}, {e.end.y:.4f}")
                if hasattr(e, 'center'):
                    self._echo(f"     Center: {e.center.x:.4f}, {e.center.y:.4f}")
                if hasattr(e, 'radius'):
                    self._echo(f"     Radius: {e.radius:.4f}")
                if hasattr(e, 'content'):
                    self._echo(f"     Text: \"{e.content}\"")
                self._echo("Command:")
                return
        # No entity found — show point coords
        self._echo(f"ID point: X={pt.x:.4f}  Y={pt.y:.4f}")
        self._echo("Command:")
