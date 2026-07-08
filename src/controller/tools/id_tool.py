from src.controller.tools.base_tool import BaseTool
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor


class IdTool(BaseTool):
    """ID command: pick a point or entity to display properties (AutoCAD-style)."""

    def __init__(self, view, document, echo_fn):
        super().__init__(view, document)
        self._echo = echo_fn

    def cursor(self):
        return QCursor(Qt.CursorShape.WhatsThisCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)

        # Try entity under cursor
        items = self.view.scene().items(scene_pos)
        entity_items = [it for it in items if hasattr(it, 'entity') and hasattr(it.entity, 'uuid')]

        if entity_items:
            e = entity_items[0].entity
            t = type(e).__name__
            self._echo(f"ID  [{t}]  Layer={e.layer_name}  Color={e.color}  Linetype={e.linetype}")
            self._echo(f"     UUID = {e.uuid}")

            if t == "Line":
                self._echo(f"     Start = {e.start.x:.4f}, {e.start.y:.4f}")
                self._echo(f"     End   = {e.end.x:.4f}, {e.end.y:.4f}")
                self._echo(f"     Length = {e.length():.4f}")
                self._echo(f"     Angle  = {self._angle(e.start, e.end):.2f} deg")
            elif t == "Circle":
                self._echo(f"     Center = {e.center.x:.4f}, {e.center.y:.4f}")
                self._echo(f"     Radius = {e.radius:.4f}")
                self._echo(f"     Circumference = {2 * 3.14159 * e.radius:.4f}")
            elif t == "Arc":
                self._echo(f"     Center = {e.center.x:.4f}, {e.center.y:.4f}")
                self._echo(f"     Radius = {e.radius:.4f}")
                import math
                sa = math.degrees(e.start_angle) % 360
                ea = math.degrees(e.end_angle) % 360
                self._echo(f"     Start angle = {sa:.2f} deg")
                self._echo(f"     End angle   = {ea:.2f} deg")
            elif t == "Polyline":
                self._echo(f"     Vertices = {len(e.vertices)}")
                self._echo(f"     Closed   = {e.is_closed}")
                self._echo(f"     Length   = {e.length():.4f}")
            elif t == "Ellipse":
                self._echo(f"     Center      = {e.center.x:.4f}, {e.center.y:.4f}")
                self._echo(f"     Major axis  = {e.major_axis.x:.4f}, {e.major_axis.y:.4f}")
                self._echo(f"     Ratio       = {e.ratio:.4f}")
            elif t == "TextEntity":
                self._echo(f"     Position = {e.position.x:.4f}, {e.position.y:.4f}")
                self._echo(f"     Content  = \"{e.content}\"")
                self._echo(f"     Height   = {e.height:.4f}")
            elif t == "PointEntity":
                self._echo(f"     Position = {e.position.x:.4f}, {e.position.y:.4f}")
            elif t == "Dimension":
                import math
                self._echo(f"     Type     = {e.dim_type}")
                self._echo(f"     Distance = {e.measured_distance():.4f}")
        else:
            self._echo(f"ID point:  X = {pt.x:.4f}  Y = {pt.y:.4f}")

        self._echo("Command:")

    @staticmethod
    def _angle(a, b) -> float:
        import math
        ang = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
        return ang % 360
