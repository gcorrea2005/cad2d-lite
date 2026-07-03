from src.model.entities.base import CadEntity, Point
import math


class Circle(CadEntity):
    def __init__(self, center: Point, radius: float, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.radius = radius

    def point_at_angle(self, angle_rad: float) -> Point:
        return Point(
            self.center.x + self.radius * math.cos(angle_rad),
            self.center.y + self.radius * math.sin(angle_rad),
        )

    def bounding_box(self) -> tuple[Point, Point]:
        return (
            Point(self.center.x - self.radius, self.center.y - self.radius),
            Point(self.center.x + self.radius, self.center.y + self.radius),
        )

    def to_dict(self) -> dict:
        return {
            "type": "Circle",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "center": [self.center.x, self.center.y],
            "radius": self.radius,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Circle":
        return cls(
            center=Point(*data["center"]),
            radius=data["radius"],
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "#FFFFFF"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
