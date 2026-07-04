from src.model.entities.base import CadEntity, Point


class TextEntity(CadEntity):
    def __init__(self, position: Point, content: str, *,
                 height: float = 2.5, rotation: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        self.content = content
        self.height = height
        self.rotation = rotation

    def bounding_box(self) -> tuple[Point, Point]:
        w = self.height * 0.6 * len(self.content)
        return (
            Point(self.position.x, self.position.y),
            Point(self.position.x + w, self.position.y + self.height),
        )

    def to_dict(self) -> dict:
        return {
            "type": "Text",
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype,
            "position": [self.position.x, self.position.y],
            "content": self.content,
            "height": self.height,
            "rotation": self.rotation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TextEntity":
        return cls(
            position=Point(*data["position"]),
            content=data["content"],
            height=data.get("height", 2.5),
            rotation=data.get("rotation", 0.0),
            uuid=data.get("uuid"),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "7"),
            linetype=data.get("linetype", "CONTINUOUS"),
        )
