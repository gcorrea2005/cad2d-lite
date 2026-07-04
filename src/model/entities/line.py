from src.model.entities.base import CadEntity, Point


class Line(CadEntity):
    def __init__(self, start: Point, end: Point, **kwargs):
        super().__init__(**kwargs)
        self.start = start
        self.end = end

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def midpoint(self) -> Point:
        return self.start.midpoint(self.end)

    def bounding_box(self) -> tuple[Point, Point]:
        return (
            Point(min(self.start.x, self.end.x), min(self.start.y, self.end.y)),
            Point(max(self.start.x, self.end.x), max(self.start.y, self.end.y)),
        )

    def to_dict(self) -> dict:
        return {
            "type": "Line",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "start": [self.start.x, self.start.y],
            "end": [self.end.x, self.end.y],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Line":
        return cls(
            start=Point(*data["start"]),
            end=Point(*data["end"]),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "7"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
