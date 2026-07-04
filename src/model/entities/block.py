"""Block entity — group of entities that can be inserted as instances."""
import copy
import math
from src.model.entities.base import Point, CadEntity


class BlockDefinition:
    """A named collection of entities that form a reusable block."""
    def __init__(self, name: str, entities: list[CadEntity], base_point: Point):
        self.name = name
        self.entities = entities
        self.base_point = base_point

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "base_point": [self.base_point.x, self.base_point.y],
            "entities": [e.to_dict() for e in self.entities],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BlockDefinition":
        from src.model.entities import ENTITY_CLASSES
        entities = []
        for ed in data["entities"]:
            etype = ed.get("type")
            if etype in ENTITY_CLASSES:
                entities.append(ENTITY_CLASSES[etype].from_dict(ed))
        bp = data["base_point"]
        return cls(data["name"], entities, Point(bp[0], bp[1]))


class BlockInstance(CadEntity):
    """An instance of a block placed in the drawing."""
    def __init__(self, block_name: str, insertion_point: Point,
                 scale_x: float = 1.0, scale_y: float = 1.0,
                 rotation: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.block_name = block_name
        self.insertion_point = insertion_point
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotation = rotation  # degrees

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["block_name"] = self.block_name
        d["insertion_point"] = [self.insertion_point.x, self.insertion_point.y]
        d["scale_x"] = self.scale_x
        d["scale_y"] = self.scale_y
        d["rotation"] = self.rotation
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "BlockInstance":
        ip = data["insertion_point"]
        return cls(
            block_name=data["block_name"],
            insertion_point=Point(ip[0], ip[1]),
            scale_x=data.get("scale_x", 1.0),
            scale_y=data.get("scale_y", 1.0),
            rotation=data.get("rotation", 0.0),
            layer_name=data.get("layer_name", "0"),
            color=data.get("color", "7"),
            uuid=data.get("uuid"),
        )

    def get_transformed_entities(self, definition: BlockDefinition) -> list[CadEntity]:
        """Generate entity copies transformed to this instance's position/scale/rotation."""
        import copy
        result = []
        rad = math.radians(self.rotation)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        bp = definition.base_point

        for ent in definition.entities:
            e = copy.deepcopy(ent)
            # Transform: translate to origin, scale, rotate, translate to insertion point
            if hasattr(e, 'start') and hasattr(e, 'end'):
                e.start = self._transform_point(e.start, bp, cos_r, sin_r)
                e.end = self._transform_point(e.end, bp, cos_r, sin_r)
            if hasattr(e, 'center'):
                e.center = self._transform_point(e.center, bp, cos_r, sin_r)
            # Scale radius for circles
            if hasattr(e, 'radius'):
                e.radius *= self.scale_x
            result.append(e)

        return result

    def bounding_box(self) -> tuple[Point, Point]:
        """Return bounding box of insertion point."""
        return (
            Point(self.insertion_point.x - 1, self.insertion_point.y - 1),
            Point(self.insertion_point.x + 1, self.insertion_point.y + 1),
        )

    def _transform_point(self, pt: Point, bp: Point, cos_r: float, sin_r: float) -> Point:
        """Apply block transform to a point."""
        # Translate to origin relative to base point
        dx = (pt.x - bp.x) * self.scale_x
        dy = (pt.y - bp.y) * self.scale_y
        # Rotate
        rx = dx * cos_r - dy * sin_r
        ry = dx * sin_r + dy * cos_r
        # Translate to insertion point
        return Point(self.insertion_point.x + rx, self.insertion_point.y + ry)
