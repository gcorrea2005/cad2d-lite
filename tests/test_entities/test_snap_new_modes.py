"""Tests for new OSNAP modes: INT, QUA, PER, TAN, NOD, INS."""
import math
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.text import TextEntity
from src.model.entities.point_entity import PointEntity
from src.model.snap import SnapEngine, SnapType


# ── NODE ──

def test_snap_node():
    pt = PointEntity(Point(5, 5))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(5.2, 5.1), [pt], {SnapType.NODE})
    assert result is not None
    assert result.snap_type == SnapType.NODE
    assert result.point == Point(5, 5)


# ── QUADRANT ──

def test_snap_quadrant_circle():
    c = Circle(Point(10, 10), 5)
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(15.2, 10.1), [c], {SnapType.QUADRANT})
    assert result is not None
    assert result.snap_type == SnapType.QUADRANT
    assert result.point == Point(15, 10)  # right quadrant


def test_snap_quadrant_arc():
    arc = Arc(Point(0, 0), 10, 0, math.pi)  # top half circle
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(10.2, 0.1), [arc], {SnapType.QUADRANT})
    assert result is not None
    assert result.snap_type == SnapType.QUADRANT
    assert result.point == Point(10, 0)


def test_snap_quadrant_arc_excludes_points_outside():
    arc = Arc(Point(0, 0), 10, 0, 0.5)  # small arc in Q1
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(-10.2, 0), [arc], {SnapType.QUADRANT})
    assert result is None  # left quadrant excluded


# ── INTERSECTION ──

def test_snap_intersection_lines():
    a = Line(Point(0, 0), Point(10, 10))
    b = Line(Point(0, 10), Point(10, 0))
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(5.2, 5.1), [a, b], {SnapType.INTERSECTION})
    assert result is not None
    assert result.snap_type == SnapType.INTERSECTION
    assert abs(result.point.x - 5) < 0.01
    assert abs(result.point.y - 5) < 0.01


def test_snap_intersection_line_circle():
    line = Line(Point(0, 5), Point(10, 5))
    circle = Circle(Point(5, 5), 3)
    engine = SnapEngine(snap_distance=1.0)
    # Near the right intersection point (8, 5)
    result = engine.find_snap(Point(8.2, 5.1), [line, circle], {SnapType.INTERSECTION})
    assert result is not None
    assert result.snap_type == SnapType.INTERSECTION
    assert abs(result.point.x - 8) < 0.5
    assert abs(result.point.y - 5) < 0.5


# ── PERPENDICULAR ──

def test_snap_perpendicular_line():
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=10.0)
    result = engine.find_snap(Point(5, 4), [line], {SnapType.PERPENDICULAR})
    assert result is not None
    assert result.snap_type == SnapType.PERPENDICULAR
    assert result.point == Point(5, 0)


def test_snap_perpendicular_circle():
    c = Circle(Point(0, 0), 10)
    engine = SnapEngine(snap_distance=15.0)
    result = engine.find_snap(Point(0, 20), [c], {SnapType.PERPENDICULAR})
    assert result is not None
    assert result.snap_type == SnapType.PERPENDICULAR
    assert result.point == Point(0, 10)


# ── TANGENT ──

def test_snap_tangent_circle():
    c = Circle(Point(0, 0), 5)
    engine = SnapEngine(snap_distance=25.0)
    result = engine.find_snap(Point(0, 20), [c], {SnapType.TANGENT})
    assert result is not None
    assert result.snap_type == SnapType.TANGENT
    # tangent point should be on the circle
    d = result.point.distance_to(c.center)
    assert abs(d - c.radius) < 0.001


def test_snap_tangent_inside_circle_returns_none():
    c = Circle(Point(0, 0), 10)
    engine = SnapEngine(snap_distance=2.0)
    result = engine.find_snap(Point(2, 3), [c], {SnapType.TANGENT})
    assert result is None  # cursor inside circle


# ── INSERTION ──

def test_snap_insertion_text():
    t = TextEntity(Point(5, 5), "hello")
    engine = SnapEngine(snap_distance=1.0)
    result = engine.find_snap(Point(5.3, 5.2), [t], {SnapType.INSERTION})
    assert result is not None
    assert result.snap_type == SnapType.INSERTION
    assert result.point == Point(5, 5)


# ── Priority checks ──

def test_intersection_priority_over_nearest():
    a = Line(Point(0, 0), Point(10, 0))
    b = Line(Point(5, -5), Point(5, 5))
    engine = SnapEngine(snap_distance=3.0)
    result = engine.find_snap(Point(5, 1), [a, b],
                               {SnapType.INTERSECTION, SnapType.NEAREST})
    assert result is not None
    assert result.snap_type == SnapType.INTERSECTION, \
        f"Expected INTERSECTION priority, got {result.snap_type}"

