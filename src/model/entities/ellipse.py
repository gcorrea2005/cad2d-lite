"""Ellipse entity."""
from src.model.entities.base import Point, CadEntity
import math


class Ellipse(CadEntity):
    def __init__(self, center: Point, major_axis: Point, ratio: float, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.major_axis = major_axis  # endpoint of major axis
        self.ratio = ratio  # minor/major ratio

    @property
    def major_radius(self) -> float:
        return self.center.distance_to(self.major_axis)

    @property
    def minor_radius(self) -> float:
        return self.major_radius * self.ratio

    @property
    def angle(self) -> float:
        """Rotation angle of major axis in radians."""
        return math.atan2(self.major_axis.y - self.center.y,
                          self.major_axis.x - self.center.x)

    def bounding_box(self) -> tuple[Point, Point]:
        r_maj = self.major_radius
        r_min = self.minor_radius
        return (
            Point(self.center.x - r_maj, self.center.y - r_maj),
            Point(self.center.x + r_maj, self.center.y + r_maj),
        )

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "center": [self.center.x, self.center.y],
            "major_axis": [self.major_axis.x, self.major_axis.y],
            "ratio": self.ratio,
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Ellipse":
        return cls(
            center=Point(data["center"][0], data["center"][1]),
            major_axis=Point(data["major_axis"][0], data["major_axis"][1]),
            ratio=data["ratio"],
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "7"),
            uuid=data.get("uuid"),
        )
