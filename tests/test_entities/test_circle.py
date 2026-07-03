from src.model.entities.base import Point
from src.model.entities.circle import Circle
import math


def test_circle_creation():
    c = Circle(center=Point(5, 5), radius=10)
    assert c.center == Point(5, 5)
    assert c.radius == 10

def test_circle_bounding_box():
    c = Circle(center=Point(5, 5), radius=10)
    bmin, bmax = c.bounding_box()
    assert bmin == Point(-5, -5)
    assert bmax == Point(15, 15)

def test_circle_point_at_angle():
    c = Circle(center=Point(0, 0), radius=10)
    p = c.point_at_angle(0)
    assert math.isclose(p.x, 10, rel_tol=1e-9)
    assert math.isclose(p.y, 0, rel_tol=1e-9)

def test_circle_serialization():
    c = Circle(center=Point(1, 2), radius=3.5, layer_name="circles")
    d = c.to_dict()
    c2 = Circle.from_dict(d)
    assert c2.center == c.center
    assert c2.radius == c.radius
    assert c2.layer_name == "circles"
