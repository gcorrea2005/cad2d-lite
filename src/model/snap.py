from dataclasses import dataclass
from enum import Enum, auto
import math
from src.model.entities.base import Point, CadEntity
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline


class SnapType(Enum):
    ENDPOINT = auto()
    MIDPOINT = auto()
    CENTER = auto()
    NEAREST = auto()
    INTERSECTION = auto()
    GRID = auto()


@dataclass
class SnapResult:
    point: Point
    snap_type: SnapType
    entity: CadEntity | None = None


class SnapEngine:
    def __init__(self, snap_distance: float = 10.0):
        self.snap_distance = snap_distance

    def find_snap(self, cursor: Point, entities: list[CadEntity],
                  active_snaps: set[SnapType]) -> SnapResult | None:
        candidates: list[SnapResult] = []

        for ent in entities:
            if SnapType.ENDPOINT in active_snaps:
                for pt in self._endpoints(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.ENDPOINT, ent))

            if SnapType.MIDPOINT in active_snaps:
                for pt in self._midpoints(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.MIDPOINT, ent))

            if SnapType.CENTER in active_snaps:
                for pt in self._centers(ent):
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.CENTER, ent))

            if SnapType.NEAREST in active_snaps:
                pt = self._nearest_point(ent, cursor)
                if pt is not None:
                    d = cursor.distance_to(pt)
                    if d <= self.snap_distance:
                        candidates.append(SnapResult(pt, SnapType.NEAREST, ent))

        if not candidates:
            return None

        candidates.sort(key=lambda r: cursor.distance_to(r.point))
        return candidates[0]

    def _endpoints(self, ent: CadEntity) -> list[Point]:
        if isinstance(ent, Line):
            return [ent.start, ent.end]
        if isinstance(ent, Arc):
            return [ent.start_point(), ent.end_point()]
        if isinstance(ent, Polyline):
            return [ent.vertices[0], ent.vertices[-1]]
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
