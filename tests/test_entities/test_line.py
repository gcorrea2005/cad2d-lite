from src.model.entities.base import Point
from src.model.entities.line import Line


def test_line_creation():
    l = Line(Point(0, 0), Point(10, 10))
    assert l.start == Point(0, 0)
    assert l.end == Point(10, 10)

def test_line_length():
    l = Line(Point(0, 0), Point(3, 4))
    assert l.length() == 5.0

def test_line_midpoint():
    l = Line(Point(0, 0), Point(10, 0))
    assert l.midpoint() == Point(5, 0)

def test_line_bounding_box():
    l = Line(Point(0, 5), Point(10, 0))
    bmin, bmax = l.bounding_box()
    assert bmin == Point(0, 0)
    assert bmax == Point(10, 5)

def test_line_serialization_roundtrip():
    l = Line(Point(1.5, 2.5), Point(3.5, 4.5), layer_name="walls", color="#FF0000")
    d = l.to_dict()
    l2 = Line.from_dict(d)
    assert l2.start == l.start
    assert l2.end == l.end
    assert l2.layer_name == "walls"
    assert l2.color == "#FF0000"
