from src.model.entities.base import Point
from src.model.entities.dimension import Dimension


def test_dimension_creation():
    d = Dimension(def_point1=Point(0, 0), def_point2=Point(10, 0),
                  text_position=Point(5, 5))
    assert d.def_point1 == Point(0, 0)
    assert d.measured_distance() == 10.0

def test_dimension_measured_distance():
    d = Dimension(def_point1=Point(0, 0), def_point2=Point(3, 4),
                  text_position=Point(1.5, 6),
                  dim_type="aligned")
    assert d.measured_distance() == 5.0

def test_dimension_serialization():
    d = Dimension(def_point1=Point(1, 2), def_point2=Point(7, 2),
                  text_position=Point(4, 4))
    d2 = Dimension.from_dict(d.to_dict())
    assert d2.def_point1 == d.def_point1
    assert d2.def_point2 == d.def_point2
