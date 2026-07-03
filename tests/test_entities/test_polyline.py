from src.model.entities.base import Point
from src.model.entities.polyline import Polyline
import pytest


def test_polyline_creation():
    pl = Polyline([Point(0, 0), Point(10, 0), Point(10, 10)])
    assert len(pl.vertices) == 3
    assert pl.is_closed is False

def test_polyline_min_vertices():
    with pytest.raises(ValueError):
        Polyline([Point(0, 0)])

def test_polyline_closed():
    pl = Polyline([Point(0, 0), Point(10, 0), Point(10, 10)], closed=True)
    assert pl.is_closed is True
    assert len(pl.segments()) == 3

def test_polyline_segments():
    pl = Polyline([Point(0, 0), Point(10, 0), Point(10, 10)])
    segs = pl.segments()
    assert len(segs) == 2
    assert segs[0] == (Point(0, 0), Point(10, 0))

def test_polyline_length():
    pl = Polyline([Point(0, 0), Point(3, 0), Point(3, 4)])
    assert pl.length() == 7.0

def test_polyline_bounding_box():
    pl = Polyline([Point(0, 5), Point(10, 0), Point(5, 10)])
    bmin, bmax = pl.bounding_box()
    assert bmin == Point(0, 0)
    assert bmax == Point(10, 10)

def test_polyline_serialization():
    pl = Polyline([Point(1, 2), Point(3, 4)], closed=True, layer_name="poly")
    d = pl.to_dict()
    pl2 = Polyline.from_dict(d)
    assert pl2.vertices == pl.vertices
    assert pl2.is_closed is True
    assert pl2.layer_name == "poly"
