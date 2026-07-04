"""Hatch tool — fill closed polylines with ACAD patterns."""
from src.controller.tools.base_tool import BaseTool
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QInputDialog
from src.model.hatch_patterns import get_pattern, PATTERNS
import math


class HatchTool(BaseTool):
    """Fill closed polylines with predefined ACAD hatch patterns."""

    def cursor(self):
        return QCursor(Qt.CursorShape.PointingHandCursor)

    def mouse_press(self, event, scene_pos: QPointF):
        pt = self._snap(scene_pos)
        click_pt = Point(pt.x, pt.y)

        # 1. Try direct click on a closed Polyline
        items = self.view.scene().items(scene_pos)
        for item in items:
            if not hasattr(item, 'entity'):
                continue
            ent = item.entity
            if isinstance(ent, Polyline) and ent.is_closed:
                self._do_hatch(ent)
                return

        # 2. Boundary detection: find nearest enclosing closed polyline
        boundary = self._find_boundary(click_pt)
        if boundary:
            self._do_hatch(boundary)
        else:
            # Echo feedback
            if hasattr(self.view, 'window') and hasattr(self.view.window(), '_echo'):
                pass  # handled by _do_hatch below
            # If still nothing found, the dialog in _do_hatch won't appear
            # since we already know there's no boundary

    def _find_boundary(self, pt: Point) -> Polyline | None:
        """Find the nearest closed polyline that contains the given point."""
        candidates = []
        for ent in self.document.entities:
            if isinstance(ent, Polyline) and ent.is_closed:
                if self._point_in_polygon(pt, ent.vertices):
                    area = abs(self._polygon_area(ent.vertices))
                    candidates.append((area, ent))

        if not candidates:
            return None
        # Return the smallest enclosing polyline (innermost boundary)
        candidates.sort()
        return candidates[0][1]

    def _point_in_polygon(self, pt: Point, vertices: list[Point]) -> bool:
        """Ray casting: is point inside polygon?"""
        x, y = pt.x, pt.y
        inside = False
        n = len(vertices)
        j = n - 1
        for i in range(n):
            xi, yi = vertices[i].x, vertices[i].y
            xj, yj = vertices[j].x, vertices[j].y
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def _polygon_area(self, vertices: list[Point]) -> float:
        """Signed polygon area (shoelace formula)."""
        area = 0.0
        n = len(vertices)
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i].x * vertices[j].y
            area -= vertices[j].x * vertices[i].y
        return area / 2.0

    def _do_hatch(self, boundary: Polyline):
        """Ask for pattern and hatch the boundary."""
        pattern_names = list(PATTERNS.keys())
        pattern_name, ok = QInputDialog.getItem(
            self.view, "Hatch Pattern", "Pattern:",
            pattern_names, 0, False)
        if not ok:
            return

        pattern = get_pattern(pattern_name)
        if not pattern:
            return

        self._hatch_polyline(boundary, pattern)

    def _hatch_polyline(self, pl: Polyline, pattern: dict):
        """Fill closed polyline with hatch pattern lines."""
        if not pattern["lines"]:
            return

        bmin, bmax = pl.bounding_box()
        diag = math.hypot(bmax.x - bmin.x, bmax.y - bmin.y)
        margin = 20
        x0, y0 = bmin.x - margin, bmin.y - margin

        for angle_deg, spacing, offset in pattern["lines"]:
            angle = math.radians(angle_deg)
            dx_line = math.cos(angle)
            dy_line = math.sin(angle)
            nx = -math.sin(angle)
            ny = math.cos(angle)

            t = offset
            while t < diag * 2:
                rx = x0 + t * nx
                ry = y0 + t * ny

                hl_start = Point(rx - diag * dx_line, ry - diag * dy_line)
                hl_end = Point(rx + diag * dx_line, ry + diag * dy_line)

                intersections = []
                for a, b in pl.segments():
                    inter = _seg_intersection(hl_start, hl_end, a, b)
                    if inter:
                        intersections.append(inter)

                intersections.sort(key=lambda p: p.x * dx_line + p.y * dy_line)

                for i in range(0, len(intersections) - 1, 2):
                    if i + 1 < len(intersections):
                        seg = Line(intersections[i], intersections[i + 1],
                                   layer_name=pl.layer_name,
                                   color=pl.color,
                                   linetype=pl.linetype)
                        self.document.add_entity(seg)

                t += spacing


def _seg_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
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
