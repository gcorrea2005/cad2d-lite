from dataclasses import dataclass
from enum import Enum, auto
import math
from src.model.entities.base import Point, CadEntity
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity


class SnapType(Enum):
    ENDPOINT = auto()
    MIDPOINT = auto()
    CENTER = auto()
    NODE = auto()          # snap to Point entity
    QUADRANT = auto()      # 0/90/180/270 deg on circle/arc
    INTERSECTION = auto()
    INSERTION = auto()     # text insertion point
    PERPENDICULAR = auto() # foot of perpendicular
    TANGENT = auto()       # tangent point on circle/arc
    NEAREST = auto()
    QUICK = auto()         # accept first found (not closest/best)
    GRID = auto()


@dataclass
class SnapResult:
    point: Point
    snap_type: SnapType
    entity: CadEntity | None = None


# ── OSMODE ↔ SnapType mapping (AutoCAD-compatible bitmask) ────
# END=1  MID=2  CEN=4  NOD=8  QUA=16  INT=32  INS=64
# PER=128  TAN=256  NEA=512  QUI=1024
_OSMODE_MAP: dict[SnapType, int] = {
    SnapType.ENDPOINT: 1,      SnapType.MIDPOINT: 2,
    SnapType.CENTER: 4,        SnapType.NODE: 8,
    SnapType.QUADRANT: 16,     SnapType.INTERSECTION: 32,
    SnapType.INSERTION: 64,    SnapType.PERPENDICULAR: 128,
    SnapType.TANGENT: 256,     SnapType.NEAREST: 512,
}
_OSMODE_REVERSE: dict[int, SnapType] = {v: k for k, v in _OSMODE_MAP.items()}

OSMODE_NAMES: dict[str, int] = {
    "END": 1, "MID": 2, "CEN": 4, "NOD": 8,
    "QUA": 16, "INT": 32, "INS": 64,
    "PER": 128, "TAN": 256, "NEA": 512, "QUI": 1024,
}


def osmode_to_snaps(osmode: int) -> set[SnapType]:
    """Convert AutoCAD OSMODE integer to set of SnapTypes."""
    snaps = set()
    for bit, st in _OSMODE_REVERSE.items():
        if osmode & bit:
            snaps.add(st)
    return snaps


def snaps_to_osmode(snaps: set[SnapType]) -> int:
    """Convert set of SnapTypes to OSMODE integer."""
    val = 0
    for st in snaps:
        val |= _OSMODE_MAP.get(st, 0)
    return val


class SnapEngine:
    _PRIORITY = {
        SnapType.ENDPOINT: 0,
        SnapType.MIDPOINT: 1,
        SnapType.CENTER: 2,
        SnapType.NODE: 3,
        SnapType.QUADRANT: 4,
        SnapType.INTERSECTION: 5,
        SnapType.INSERTION: 6,
        SnapType.PERPENDICULAR: 7,
        SnapType.TANGENT: 8,
        SnapType.NEAREST: 9,
        SnapType.GRID: 10,  # lowest priority: always overridden by geometry snaps
    }

    def __init__(self, snap_distance: float = 10.0):
        self.snap_distance = snap_distance

    def find_snap(self, cursor: Point, entities: list[CadEntity],
                  active_snaps: set[SnapType],
                  ref_point: Point | None = None) -> SnapResult | None:
        """Find best snap. ref_point = first point of line-in-progress (for PER/TAN)."""
        quick = SnapType.QUICK in active_snaps
        candidates: list[SnapResult] = []

        for ent in entities:
            if SnapType.ENDPOINT in active_snaps:
                for pt in self._endpoints(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.ENDPOINT, ent))
                        if quick: break

            if SnapType.MIDPOINT in active_snaps:
                for pt in self._midpoints(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.MIDPOINT, ent))
                        if quick: break

            if SnapType.CENTER in active_snaps:
                for pt in self._centers(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.CENTER, ent))
                        if quick: break

            if SnapType.NODE in active_snaps:
                for pt in self._nodes(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.NODE, ent))
                        if quick: break

            if SnapType.QUADRANT in active_snaps:
                for pt in self._quadrants(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.QUADRANT, ent))
                        if quick: break

            if SnapType.INSERTION in active_snaps:
                for pt in self._insertion_points(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.INSERTION, ent))
                        if quick: break

            if SnapType.INTERSECTION in active_snaps:
                for other in entities:
                    if other is ent:
                        continue
                    for pt in self._intersections(ent, other):
                        d = cursor.distance_to(pt)
                        if d <= self.snap_distance:
                            candidates.append(SnapResult(pt, SnapType.INTERSECTION, None))
                            if quick: break

            if SnapType.PERPENDICULAR in active_snaps:
                pt = self._perpendicular(ent, ref_point if ref_point else cursor)
                if pt is not None:
                    d = cursor.distance_to(pt)
                    # PER gets 2x tolerance — foot can be far from cursor
                    if d <= self.snap_distance * 2.0:
                        candidates.append(SnapResult(pt, SnapType.PERPENDICULAR, ent))
                        if quick: break

            if SnapType.TANGENT in active_snaps:
                for pt in self._tangents(ent, cursor):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.TANGENT, ent))
                        if quick: break

            if SnapType.NEAREST in active_snaps:
                pt = self._nearest_point(ent, cursor)
                if pt is not None:
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.NEAREST, ent))
                        if quick: break

        # Grid snap (always check, independent of entities)
        if SnapType.GRID in active_snaps:
            grid_pt = self._grid_snap(cursor)
            if grid_pt:
                d = cursor.distance_to(grid_pt)
                if d <= self.snap_distance:
                    candidates.append(SnapResult(grid_pt, SnapType.GRID, None))

        if not candidates:
            return None

        candidates.sort(key=lambda r: (
            self._PRIORITY.get(r.snap_type, 99),
            cursor.distance_to(r.point),
        ))
        return candidates[0]

    # ── Individual snap point collectors ────────────────────

    def _endpoints(self, ent: CadEntity) -> list[Point]:
        if isinstance(ent, Line):
            return [ent.start, ent.end]
        if isinstance(ent, Arc):
            return [ent.start_point(), ent.end_point()]
        if isinstance(ent, Polyline):
            vs = ent.vertices
            return [vs[0], vs[-1]] if vs else []
        return []

    def _midpoints(self, ent: CadEntity) -> list[Point]:
        if isinstance(ent, Line):
            return [ent.midpoint()]
        if isinstance(ent, Arc):
            return [ent.midpoint()]
        return []

    def _centers(self, ent: CadEntity) -> list[Point]:
        if isinstance(ent, Circle):
            return [ent.center]
        if isinstance(ent, Arc):
            return [ent.center]
        return []

    def _nodes(self, ent: CadEntity) -> list[Point]:
        """NODE snap: snap to Point entities."""
        from src.model.entities.point_entity import PointEntity
        if isinstance(ent, PointEntity):
            return [ent.position]
        return []

    def _quadrants(self, ent: CadEntity) -> list[Point]:
        """QUADRANT snap: 0/90/180/270 degrees on circle/arc."""
        if isinstance(ent, Circle):
            c = ent.center
            r = ent.radius
            return [Point(c.x + r, c.y), Point(c.x - r, c.y),
                    Point(c.x, c.y + r), Point(c.x, c.y - r)]
        if isinstance(ent, Arc):
            c = ent.center
            r = ent.radius
            pts = []
            for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
                px = c.x + r * math.cos(ang)
                py = c.y + r * math.sin(ang)
                pt = Point(px, py)
                if ent.contains_angle(ang):
                    pts.append(pt)
            return pts
        return []

    def _insertion_points(self, ent: CadEntity) -> list[Point]:
        """INSERTION snap: insertion/base point of text/block."""
        if isinstance(ent, TextEntity):
            return [ent.position]
        return []

    def _intersections(self, ent_a: CadEntity, ent_b: CadEntity) -> list[Point]:
        """Compute intersection points between two entities."""
        if isinstance(ent_a, Line) and isinstance(ent_b, Line):
            return self._line_line_intersect(ent_a, ent_b)
        if isinstance(ent_a, Line) and isinstance(ent_b, Circle):
            return self._line_circle_intersect(ent_a, ent_b)
        if isinstance(ent_b, Line) and isinstance(ent_a, Circle):
            return self._line_circle_intersect(ent_b, ent_a)
        if isinstance(ent_a, Circle) and isinstance(ent_b, Circle):
            return self._circle_circle_intersect(ent_a, ent_b)
        return []

    def _perpendicular(self, ent: CadEntity, ref: Point) -> Point | None:
        """PERPENDICULAR snap: foot of perpendicular from ref point to entity."""
        if isinstance(ent, Line):
            return self._foot_of_perpendicular(ent.start, ent.end, ref)
        if isinstance(ent, Polyline):
            best = None
            best_dist = float('inf')
            for seg in ent.segments():
                a, b = seg
                pt = self._foot_of_perpendicular(a, b, ref)
                d = ref.distance_to(pt)
                if d < best_dist:
                    best_dist = d
                    best = pt
            return best
        if isinstance(ent, Circle):
            dx = ref.x - ent.center.x
            dy = ref.y - ent.center.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                return ent.point_at_angle(0)
            return Point(
                ent.center.x + dx / dist * ent.radius,
                ent.center.y + dy / dist * ent.radius,
            )
        if isinstance(ent, Arc):
            dx = ref.x - ent.center.x
            dy = ref.y - ent.center.y
            ang = math.atan2(dy, dx)
            if ent.contains_angle(ang):
                return Point(
                    ent.center.x + math.cos(ang) * ent.radius,
                    ent.center.y + math.sin(ang) * ent.radius,
                )
            pts = [ent.start_point(), ent.end_point()]
            dists = [(ref.distance_to(p), p) for p in pts]
            return min(dists)[1] if dists else None
        return None

    def _tangents(self, ent: CadEntity, cursor: Point) -> list[Point]:
        """TANGENT snap: tangent points on circle/arc from cursor position."""
        if isinstance(ent, Circle):
            return self._circle_tangents_from_point(ent.center, ent.radius, cursor)
        if isinstance(ent, Arc):
            pts = self._circle_tangents_from_point(ent.center, ent.radius, cursor)
            return [p for p in pts if ent.contains_angle(
                math.atan2(p.y - ent.center.y, p.x - ent.center.x))]
        return []

    # ── Geometry helpers ────────────────────────────────────

    @staticmethod
    def _line_line_intersect(a: Line, b: Line) -> list[Point]:
        x1, y1 = a.start.x, a.start.y
        x2, y2 = a.end.x, a.end.y
        x3, y3 = b.start.x, b.start.y
        x4, y4 = b.end.x, b.end.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-10:
            return []  # parallel or coincident

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

        if 0 <= t <= 1 and 0 <= u <= 1:
            return [Point(x1 + t * (x2 - x1), y1 + t * (y2 - y1))]
        return []

    @staticmethod
    def _line_circle_intersect(line: Line, circle: Circle) -> list[Point]:
        """Line segment vs circle intersection."""
        cx, cy, r = circle.center.x, circle.center.y, circle.radius
        x1, y1 = line.start.x, line.start.y
        x2, y2 = line.end.x, line.end.y

        dx = x2 - x1
        dy = y2 - y1
        fx = x1 - cx
        fy = y1 - cy

        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - r * r

        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        if a < 1e-10:
            return []

        pts = []
        sqrt_disc = math.sqrt(disc)
        for sign in (-1, 1):
            t = (-b + sign * sqrt_disc) / (2 * a)
            if 0 <= t <= 1:
                pts.append(Point(x1 + t * dx, y1 + t * dy))
        return pts

    @staticmethod
    def _circle_circle_intersect(a: Circle, b: Circle) -> list[Point]:
        dx = b.center.x - a.center.x
        dy = b.center.y - a.center.y
        d = math.hypot(dx, dy)
        if d < 1e-10 or d > a.radius + b.radius or d < abs(a.radius - b.radius):
            return []

        a2 = a.radius * a.radius
        x = (d * d - b.radius * b.radius + a2) / (2 * d)
        y_sq = a2 - x * x
        if y_sq < 0:
            return []

        y = math.sqrt(y_sq)
        mid_x = a.center.x + dx * x / d
        mid_y = a.center.y + dy * x / d
        perp_x = -dy * y / d
        perp_y = dx * y / d

        return [Point(mid_x + perp_x, mid_y + perp_y),
                Point(mid_x - perp_x, mid_y - perp_y)]

    @staticmethod
    def _circle_tangents_from_point(center: Point, r: float, cursor: Point) -> list[Point]:
        """Compute tangent points on circle from external cursor point."""
        dx = cursor.x - center.x
        dy = cursor.y - center.y
        d_sq = dx * dx + dy * dy
        r_sq = r * r
        if d_sq < r_sq:
            return []  # cursor inside circle — no tangents

        th = math.atan2(dy, dx)
        dh = math.acos(r / math.sqrt(d_sq)) if d_sq > r_sq else 0

        pts = []
        for sign in (-1, 1):
            ang = th + sign * dh
            pts.append(Point(center.x + r * math.cos(ang),
                             center.y + r * math.sin(ang)))
        return pts

    @staticmethod
    def _foot_of_perpendicular(a: Point, b: Point, p: Point) -> Point:
        """Foot of perpendicular from point p onto line segment ab."""
        dx, dy = b.x - a.x, b.y - a.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return a
        t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / length_sq
        # clamp to segment
        t = max(0.0, min(1.0, t))
        return Point(a.x + t * dx, a.y + t * dy)

    def _nearest_point(self, ent: CadEntity, cursor: Point) -> Point | None:
        if isinstance(ent, Line):
            return self._nearest_on_line(ent.start, ent.end, cursor)
        if isinstance(ent, Circle):
            dx = cursor.x - ent.center.x
            dy = cursor.y - ent.center.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                return ent.point_at_angle(0)
            return Point(
                ent.center.x + dx / dist * ent.radius,
                ent.center.y + dy / dist * ent.radius,
            )
        return None

    @staticmethod
    def _nearest_on_line(a: Point, b: Point, p: Point) -> Point:
        dx, dy = b.x - a.x, b.y - a.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return a
        t = max(0, min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / length_sq))
        return Point(a.x + t * dx, a.y + t * dy)

    def _grid_snap(self, cursor: Point) -> Point | None:
        """Snap cursor to nearest grid point using SNAPUNIT."""
        try:
            sx = sy = 1.0
            if hasattr(self, '_snap_unit'):
                sx, sy = self._snap_unit
            gx = round(cursor.x / sx) * sx
            gy = round(cursor.y / sy) * sy
            return Point(gx, gy)
        except Exception:
            return None
