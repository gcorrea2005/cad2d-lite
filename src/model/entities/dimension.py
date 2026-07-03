from src.model.entities.base import CadEntity, Point


class Dimension(CadEntity):
    def __init__(self, def_point1: Point, def_point2: Point,
                 text_position: Point, **kwargs):
        super().__init__(**kwargs)
        self.def_point1 = def_point1
        self.def_point2 = def_point2
        self.text_position = text_position

    def measured_distance(self) -> float:
        return self.def_point1.distance_to(self.def_point2)

    def bounding_box(self) -> tuple[Point, Point]:
        pts = [self.def_point1, self.def_point2, self.text_position]
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        return (Point(min(xs), min(ys)), Point(max(xs), max(ys)))

    def to_dict(self) -> dict:
        return {
            "type": "Dimension",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "def_point1": [self.def_point1.x, self.def_point1.y],
            "def_point2": [self.def_point2.x, self.def_point2.y],
            "text_position": [self.text_position.x, self.text_position.y],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dimension":
        return cls(
            def_point1=Point(*data["def_point1"]),
            def_point2=Point(*data["def_point2"]),
            text_position=Point(*data["text_position"]),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "#FFFFFF"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
