from src.model.entities.base import CadEntity, Point
import math


class Arc(CadEntity):
    def __init__(self, center: Point, radius: float, start_angle: float,
                 end_angle: float, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def start_point(self) -> Point:
        return Point(self.center.x + self.radius * math.cos(self.start_angle),
                     self.center.y + self.radius * math.sin(self.start_angle))

    def end_point(self) -> Point:
        return Point(self.center.x + self.radius * math.cos(self.end_angle),
                     self.center.y + self.radius * math.sin(self.end_angle))

    def midpoint(self) -> Point:
        mid_angle = (self.start_angle + self.end_angle) / 2
        return Point(self.center.x + self.radius * math.cos(mid_angle),
                     self.center.y + self.radius * math.sin(mid_angle))

    def bounding_box(self) -> tuple[Point, Point]:
        pts = [self.start_point(), self.end_point()]
        start = self.start_angle % (2 * math.pi)
        end = self.end_angle % (2 * math.pi)
        if end < start:
            end += 2 * math.pi
        for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
            a = angle
            while a < start:
                a += 2 * math.pi
            if start <= a <= end:
                pts.append(Point(
                    self.center.x + self.radius * math.cos(angle),
                    self.center.y + self.radius * math.sin(angle),
                ))
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        return (Point(min(xs), min(ys)), Point(max(xs), max(ys)))

    def to_dict(self) -> dict:
        return {
            "type": "Arc",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "center": [self.center.x, self.center.y],
            "radius": self.radius,
            "start_angle": self.start_angle,
            "end_angle": self.end_angle,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Arc":
        return cls(
            center=Point(*data["center"]),
            radius=data["radius"],
            start_angle=data["start_angle"],
            end_angle=data["end_angle"],
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "#FFFFFF"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
