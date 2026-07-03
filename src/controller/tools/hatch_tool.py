from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
import math


class HatchTool(BaseTool):
    """Basic hatch: fill closed polyline area with parallel lines."""
    def cursor(self):
        return QCursor(Qt.CursorShape.PointingHandCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        # Ask for spacing and angle
        spacing, ok = QInputDialog.getDouble(
            self.view, "Hatch", "Line spacing:", 1.0, 0.1, 100, 2)
        if not ok:
            return
        angle_deg, ok = QInputDialog.getDouble(
            self.view, "Hatch", "Angle (degrees):", 45.0, 0, 360, 1)
        if not ok:
            return

        angle = math.radians(angle_deg)

        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Polyline) and ent.is_closed:
                self._hatch_polyline(ent, spacing, angle)
                break

    def _hatch_polyline(self, pl: Polyline, spacing: float, angle: float):
        """Fill closed polyline with parallel hatch lines."""
        bmin, bmax = pl.bounding_box()
        margin = spacing * 2
        x0 = bmin.x - margin
        y0 = bmin.y - margin
        x1 = bmax.x + margin
        y1 = bmax.y + margin

        # Direction perpendicular to hatch lines
        nx = math.cos(angle + math.pi / 2)
        ny = math.sin(angle + math.pi / 2)
        # Hatch line direction
        dx_line = math.cos(angle)
        dy_line = math.sin(angle)

        # Extent along normal direction
        diag = math.hypot(x1 - x0, y1 - y0)

        # Generate hatch lines
        t = 0.0
        while t < diag * 2:
            # Reference point for this hatch line
            rx = x0 + t * nx
            ry = y0 + t * ny

            # Create a long line through the bbox
            hl_start = Point(rx - diag * dx_line, ry - diag * dy_line)
            hl_end = Point(rx + diag * dx_line, ry + diag * dy_line)

            # Find intersections with polyline edges
            intersections = []
            for a, b in pl.segments():
                inter = _seg_intersection(hl_start, hl_end, a, b)
                if inter:
                    intersections.append(inter)

            # Sort intersections along hatch line direction
            intersections.sort(key=lambda p: p.x * dx_line + p.y * dy_line)

            # Draw segments between pairs
            for i in range(0, len(intersections) - 1, 2):
                if i + 1 < len(intersections):
                    seg = Line(intersections[i], intersections[i + 1],
                               layer_name=pl.layer_name,
                               color="#444466")  # dim blue hatch
                    self.document.add_entity(seg)

            t += spacing


def _seg_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    """Intersection of two line segments. Returns None if no intersection."""
    dx1 = a2.x - a1.x
    dy1 = a2.y - a1.y
    dx2 = b2.x - b1.x
    dy2 = b2.y - b1.y
    denom = dx1 * dy2 - dy1 * dx2
    if abs(denom) < 0.0001:
        return None
    t = ((b1.x - a1.x) * dy2 - (b1.y - a1.y) * dx2) / denom
    u = ((b1.x - a1.x) * dy1 - (b1.y - a1.y) * dx1) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return Point(a1.x + t * dx1, a1.y + t * dy1)
    return None
