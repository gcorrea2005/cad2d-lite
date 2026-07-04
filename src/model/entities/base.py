from dataclasses import dataclass
from abc import ABC, abstractmethod
from uuid import uuid4
import math


@dataclass(frozen=True, slots=True)
class Point:
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def midpoint(self, other: "Point") -> "Point":
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)


class CadEntity(ABC):
    def __init__(self, *, layer_name: str = "0", color: str = "7",
                 linetype: str = "CONTINUOUS", uuid: str | None = None):
        self.uuid = uuid or str(uuid4())
        self.layer_name = layer_name
        self.color = color
        self.linetype = linetype

    @abstractmethod
    def bounding_box(self) -> tuple[Point, Point]:
        """Return (min_point, max_point)."""
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        return {
            "type": self.__class__.__name__,
            "uuid": self.uuid,
            "layer_name": self.layer_name,
            "color": self.color,
            "linetype": self.linetype if hasattr(self, 'linetype') else "CONTINUOUS",
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "CadEntity":
        """Deserialize from dict."""
        ...
