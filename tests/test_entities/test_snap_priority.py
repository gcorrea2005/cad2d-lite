"""
Test that ENDPOINT snap takes priority over NEAREST (AutoCAD behavior).
"""
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.snap import SnapEngine, SnapType


def test_endpoint_priority_over_nearest():
    """ENDPOINT should win over NEAREST even when NEAREST is geometrically closer."""
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=2.0)
    # Cursor at (0.8, 0.5) — closer to projected NEAREST (0.8, 0) than to ENDPOINT (0, 0)
    # Without priority: NEAREST would win (distance 0.5 vs endpoint 0.94)
    # With priority: ENDPOINT must win
    result = engine.find_snap(
        Point(0.8, 0.5), [line],
        {SnapType.ENDPOINT, SnapType.NEAREST},
    )
    assert result is not None
    assert result.snap_type == SnapType.ENDPOINT, (
        f"Expected ENDPOINT priority, got {result.snap_type}")
    assert result.point == Point(0, 0)


def test_midpoint_priority_over_nearest():
    """MIDPOINT should win over NEAREST."""
    line = Line(Point(0, 0), Point(10, 0))
    engine = SnapEngine(snap_distance=2.0)
    # Cursor near midpoint — MIDPOINT (5, 0) vs NEAREST projection
    result = engine.find_snap(
        Point(5, 0.5), [line],
        {SnapType.MIDPOINT, SnapType.NEAREST},
    )
    assert result is not None
    assert result.snap_type == SnapType.MIDPOINT
    assert result.point == Point(5, 0)
