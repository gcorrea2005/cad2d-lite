from src.model.entities.base import Point
from src.model.entities.arc import Arc
import math


def test_arc_creation():
    a = Arc(center=Point(0, 0), radius=10, start_angle=0, end_angle=math.pi)
    assert a.radius == 10

def test_arc_endpoints():
    a = Arc(center=Point(0, 0), radius=10, start_angle=0, end_angle=math.pi / 2)
    start = a.start_point()
    end = a.end_point()
    assert math.isclose(start.x, 10, abs_tol=1e-9)
    assert math.isclose(start.y, 0, abs_tol=1e-9)
    assert math.isclose(end.x, 0, abs_tol=1e-9)
    assert math.isclose(end.y, 10, abs_tol=1e-9)

def test_arc_bounding_box():
    a = Arc(center=Point(0, 0), radius=10, start_angle=0, end_angle=math.pi / 2)
    bmin, bmax = a.bounding_box()
    assert math.isclose(bmin.x, 0, abs_tol=1e-9)
    assert math.isclose(bmax.x, 10, abs_tol=1e-9)
    assert math.isclose(bmin.y, 0, abs_tol=1e-9)
    assert math.isclose(bmax.y, 10, abs_tol=1e-9)

def test_arc_midpoint():
    a = Arc(center=Point(0, 0), radius=10, start_angle=0, end_angle=math.pi / 2)
    mp = a.midpoint()
    angle = math.pi / 4
    assert math.isclose(mp.x, 10 * math.cos(angle), rel_tol=1e-9)
    assert math.isclose(mp.y, 10 * math.sin(angle), rel_tol=1e-9)

def test_arc_serialization():
    a = Arc(center=Point(1, 2), radius=5, start_angle=0.5, end_angle=2.0)
    d = a.to_dict()
    a2 = Arc.from_dict(d)
    assert a2.center == a.center
    assert a2.radius == a.radius
    assert math.isclose(a2.start_angle, a.start_angle)
    assert math.isclose(a2.end_angle, a.end_angle)
