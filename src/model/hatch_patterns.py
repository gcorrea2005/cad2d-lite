"""
Hatch pattern definitions — ACAD standard patterns rendered with QPainter.

Each pattern is defined by lines at specific angles and spacings.
"""
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPainter, QPen, QColor


# ── Pattern definitions ─────────────────────────────────────
# Each pattern: list of (angle_deg, spacing_px, offset_px) line families
PATTERNS = {
    "ANSI31": {
        "name": "ANSI31",
        "desc": "Brick / masonry",
        "lines": [(45, 4, 0)],  # 45° lines, 4px spacing
    },
    "ANSI32": {
        "name": "ANSI32",
        "desc": "Steel",
        "lines": [(45, 4, 0), (135, 4, 0)],  # cross-hatch
    },
    "ANSI33": {
        "name": "ANSI33",
        "desc": "Bronze / brass",
        "lines": [(45, 6, 0), (135, 6, 0), (0, 6, 0), (90, 6, 0)],
    },
    "ANSI34": {
        "name": "ANSI34",
        "desc": "Plastic / rubber",
        "lines": [(45, 4, 0), (135, 4, 0), (0, 4, 0)],
    },
    "ANSI35": {
        "name": "ANSI35",
        "desc": "Concrete",
        "lines": [(45, 3, 0), (135, 6, 1)],  # sand + gravel
    },
    "ANSI36": {
        "name": "ANSI36",
        "desc": "Earth",
        "lines": [(0, 3, 0), (90, 3, 0), (45, 8, 0), (135, 8, 0)],
    },
    "ANSI37": {
        "name": "ANSI37",
        "desc": "Lead / zinc",
        "lines": [(45, 6, 0), (135, 6, 0)],
    },
    "ANSI38": {
        "name": "ANSI38",
        "desc": "Aluminum",
        "lines": [(45, 3, 0), (135, 6, 0), (0, 6, 0)],
    },
    "SOLID": {
        "name": "SOLID",
        "desc": "Solid fill",
        "lines": [],
    },
}


def list_patterns() -> list[str]:
    return sorted(PATTERNS.keys())


def get_pattern(name: str) -> dict | None:
    return PATTERNS.get(name.upper())


def paint_hatch(painter: QPainter, polygon_points: list[QPointF],
                pattern_name: str, color: QColor):
    """Paint a hatch pattern inside a polygon."""
    pattern = get_pattern(pattern_name)
    if not pattern:
        return

    if pattern_name == "SOLID":
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(polygon_points)
        return

    # For line-based patterns, clip to polygon and draw lines
    painter.save()

    # Create clipping path from polygon
    path = painter.clipPath() if False else None
    poly = polygon_points

    # Compute bounding rect
    xs = [p.x() for p in poly]
    ys = [p.y() for p in poly]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w, h = max_x - min_x, max_y - min_y
    diag = (w * w + h * h) ** 0.5

    pen = QPen(color)
    pen.setWidthF(0)
    painter.setPen(pen)

    # Set clip region to polygon
    from PySide6.QtGui import QPainterPath, QPolygonF
    clip_path = QPainterPath()
    clip_path.addPolygon(QPolygonF(poly))
    painter.setClipPath(clip_path)

    import math

    for angle_deg, spacing, offset in pattern["lines"]:
        angle_rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

        # Generate parallel lines across the bounding box
        step_x = -sin_a * spacing
        step_y = cos_a * spacing

        # Start from one corner offset outward
        cx, cy = min_x, min_y
        # Walk the perpendicular direction
        for i in range(-5, int(diag / spacing) + 10):
            px = cx + step_x * i + cos_a * offset
            py = cy + step_y * i + sin_a * offset
            # Draw a line that spans the diagonal
            painter.drawLine(
                QPointF(px - cos_a * diag * 2, py - sin_a * diag * 2),
                QPointF(px + cos_a * diag * 2, py + sin_a * diag * 2),
            )

    painter.restore()
