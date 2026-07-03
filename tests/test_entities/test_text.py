from src.model.entities.base import Point
from src.model.entities.text import TextEntity


def test_text_creation():
    t = TextEntity(position=Point(10, 20), content="Hello")
    assert t.position == Point(10, 20)
    assert t.content == "Hello"
    assert t.height == 2.5

def test_text_serialization():
    t = TextEntity(position=Point(1, 2), content="Test", height=5.0)
    d = t.to_dict()
    t2 = TextEntity.from_dict(d)
    assert t2.content == "Test"
    assert t2.height == 5.0
