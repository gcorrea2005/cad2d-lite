from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.snap import SnapEngine, SnapType


def test_snap_endpoint():
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(0.3, 0.2), [line], {SnapType.ENDPOINT})
    assert result is not None
    assert result.point == Point(0, 0)
    assert result.snap_type == SnapType.ENDPOINT

def test_snap_midpoint():
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(5.1, 0.3), [line], {SnapType.MIDPOINT})
    assert result is not None
    assert result.point == Point(5, 0)

def test_snap_center():
    circle = Circle(Point(5, 5), 10)
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(5.2, 5.3), [circle], {SnapType.CENTER})
    assert result is not None
    assert result.point == Point(5, 5)

def test_snap_nearest():
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(3, 0.5), [line], {SnapType.NEAREST})
    assert result is not None
    assert result.point == Point(3, 0)

def test_snap_out_of_range():
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(3, 5), [line], {SnapType.NEAREST})
    assert result is None
