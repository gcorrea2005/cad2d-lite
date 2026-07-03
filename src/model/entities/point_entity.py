from src.model.entities.base import CadEntity, Point


class PointEntity(CadEntity):
    """A single point entity (like AutoCAD POINT)."""
    def __init__(self, position: Point, **kwargs):
        super().__init__(**kwargs)
        self.position = position

    def bounding_box(self) -> tuple[Point, Point]:
        return (self.position, self.position)

    def to_dict(self) -> dict:
        return {
            "type": "Point",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "position": [self.position.x, self.position.y],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PointEntity":
        return cls(
            position=Point(*data["position"]),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "#FFFFFF"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
