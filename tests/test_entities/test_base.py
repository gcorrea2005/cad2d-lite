from src.model.entities.base import Point, CadEntity
from uuid import UUID


class FakeEntity(CadEntity):
    def bounding_box(self):
        return (Point(), Point())
    def to_dict(self) -> dict:
        return {}
    @classmethod
    def from_dict(cls, data: dict) -> "FakeEntity":
        return cls()


def test_point_creation():
    p = Point(10.0, 20.0)
    assert p.x == 10.0
    assert p.y == 20.0

def test_point_distance():
    p1 = Point(0, 0)
    p2 = Point(3, 4)
    assert p1.distance_to(p2) == 5.0

def test_point_midpoint():
    p1 = Point(0, 0)
    p2 = Point(10, 0)
    assert p1.midpoint(p2) == Point(5, 0)

def test_point_add():
    assert Point(1, 2) + Point(3, 4) == Point(4, 6)

def test_point_sub():
    assert Point(5, 5) - Point(2, 3) == Point(3, 2)

def test_entity_has_uuid():
    e = FakeEntity(layer_name="0")
    assert isinstance(e.uuid, str)

def test_entity_default_layer():
    e = FakeEntity()
    assert e.layer_name == "0"

def test_entity_custom_properties():
    e = FakeEntity(layer_name="walls", color="#FF0000")
    assert e.layer_name == "walls"
    assert e.color == "#FF0000"

def test_entity_linetype_default():
    e = FakeEntity()
    assert e.linetype == "CONTINUOUS"
