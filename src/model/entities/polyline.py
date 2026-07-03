from src.model.entities.base import CadEntity, Point


class Polyline(CadEntity):
    def __init__(self, vertices: list[Point], *, closed: bool = False, **kwargs):
        super().__init__(**kwargs)
        if len(vertices) < 2:
            raise ValueError("Polyline requires at least 2 vertices")
        self.vertices = vertices
        self.is_closed = closed

    def segments(self) -> list[tuple[Point, Point]]:
        segs = [(self.vertices[i], self.vertices[i + 1])
                for i in range(len(self.vertices) - 1)]
        if self.is_closed:
            segs.append((self.vertices[-1], self.vertices[0]))
        return segs

    def length(self) -> float:
        return sum(a.distance_to(b) for a, b in self.segments())

    def bounding_box(self) -> tuple[Point, Point]:
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        return (Point(min(xs), min(ys)), Point(max(xs), max(ys)))

    def to_dict(self) -> dict:
        return {
            "type": "Polyline",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "vertices": [[v.x, v.y] for v in self.vertices],
            "closed": self.is_closed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Polyline":
        return cls(
            vertices=[Point(*v) for v in data["vertices"]],
            closed=data.get("closed", False),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "#FFFFFF"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
