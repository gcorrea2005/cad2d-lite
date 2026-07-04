from src.model.entities.base import CadEntity, Point


class Dimension(CadEntity):
    def __init__(self, def_point1: Point, def_point2: Point,
                 text_position: Point, *, dim_type: str = "linear", **kwargs):
        super().__init__(**kwargs)
        self.def_point1 = def_point1
        self.def_point2 = def_point2
        self.text_position = text_position
        self.dim_type = dim_type  # "linear" (H/V) or "aligned" (parallel to points)

    def measured_distance(self) -> float:
        if self.dim_type == "aligned":
            return self.def_point1.distance_to(self.def_point2)
        if self.dim_type == "radius":
            return self.def_point1.distance_to(self.def_point2)
        # linear: use horizontal or vertical distance
        dx = abs(self.def_point2.x - self.def_point1.x)
        dy = abs(self.def_point2.y - self.def_point1.y)
        return max(dx, dy)  # horizontal if dx>dy, vertical otherwise

    def angle(self) -> float:
        """Angle of the dimension line in radians."""
        import math
        return math.atan2(
            self.def_point2.y - self.def_point1.y,
            self.def_point2.x - self.def_point1.x,
        )

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
            "dim_type": self.dim_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dimension":
        return cls(
            def_point1=Point(*data["def_point1"]),
            def_point2=Point(*data["def_point2"]),
            text_position=Point(*data["text_position"]),
            dim_type=data.get("dim_type", "linear"),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "7"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
