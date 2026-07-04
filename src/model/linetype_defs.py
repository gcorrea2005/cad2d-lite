"""
Linetype definitions — AutoCAD R10 standard linetypes.

Each linetype is defined as a list of dash/gap lengths (positive=dash, negative=gap, zero=dot).
Scaled by LTSCALE at render time.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class LineType:
    name: str
    description: str
    pattern: list[float]  # positive=dash, negative=gap, 0=dot


# ── Standard ACAD linetypes ─────────────────────────────────
_STANDARD_LINETYPES: dict[str, LineType] = {
    "CONTINUOUS": LineType("CONTINUOUS", "Solid line", []),
    "DASHED":     LineType("DASHED", "Dashed __ __ __",
                           [12.7, -6.35]),
    "HIDDEN":     LineType("HIDDEN", "Hidden _ _ _ _",
                           [6.35, -3.175]),
    "CENTER":     LineType("CENTER", "Center ____ _ ____ _",
                           [31.75, -6.35, 6.35, -6.35]),
    "PHANTOM":    LineType("PHANTOM", "Phantom ______  __  ______",
                           [31.75, -6.35, 6.35, -6.35, 6.35, -6.35]),
    "DASHDOT":    LineType("DASHDOT", "Dash dot __ . __ .",
                           [12.7, -6.35, 0, -6.35]),
    "BORDER":     LineType("BORDER", "Border __ __ . __ __ .",
                           [12.7, -6.35, 12.7, -6.35, 0, -6.35]),
    "DIVIDE":     LineType("DIVIDE", "Divide __ . . __ . .",
                           [12.7, -6.35, 0, -6.35, 0, -6.35]),
    "DOT":        LineType("DOT", "Dot . . . . . . . .",
                           [0, -6.35]),
    "DOT2":       LineType("DOT2", "Dot (.5x) ...............................",
                           [0, -3.175]),
    "DOTX2":      LineType("DOTX2", "Dot (2x) .  .  .  .",
                           [0, -12.7]),
    "HIDDEN2":    LineType("HIDDEN2", "Hidden (.5x) _ _ _ _ _",
                           [3.175, -1.5875]),
    "HIDDENX2":   LineType("HIDDENX2", "Hidden (2x) ____ ____ ____",
                           [12.7, -6.35]),
    "CENTER2":    LineType("CENTER2", "Center (.5x) ________  __  ________",
                           [15.875, -3.175, 3.175, -3.175]),
    "CENTERX2":   LineType("CENTERX2", "Center (2x) ______________  ______  ______________",
                           [63.5, -12.7, 12.7, -12.7]),
}

# Aliases
_ALIASES = {
    "DASHED2": "HIDDEN",     # Dashed (.5x) is basically Hidden
    "DASHEDX2": "DASHED",    # Kept as DASHED since it's the same scale
}


def get_linetype(name: str) -> LineType:
    """Get linetype definition by name (case-insensitive)."""
    key = name.upper()
    if key in _ALIASES:
        key = _ALIASES[key]
    if key in _STANDARD_LINETYPES:
        return _STANDARD_LINETYPES[key]
    return _STANDARD_LINETYPES["CONTINUOUS"]


def list_linetypes() -> list[str]:
    """List all available linetype names."""
    return sorted(_STANDARD_LINETYPES.keys())


def get_qt_dash_pattern(entity_linetype: str, ltscale: float = 1.0) -> list[float] | None:
    """
    Return a Qt-compatible dash pattern (all positive values) for QPen.setDashPattern().
    Returns None for CONTINUOUS (solid line).
    """
    lt = get_linetype(entity_linetype)
    if not lt.pattern:
        return None  # CONTINUOUS

    # Qt expects all positive dash pattern: [dash_len, gap_len, dash_len, gap_len, ...]
    # ACAD uses positive=dash, negative=gap, zero=dot (rendered as tiny dash)
    qt_pattern = []
    for val in lt.pattern:
        abs_val = abs(val) * ltscale
        if val == 0:
            # Dot: render as a tiny dash + same tiny gap
            dot_len = max(0.5, ltscale * 0.5)
            qt_pattern.append(dot_len)
            qt_pattern.append(dot_len)
        else:
            qt_pattern.append(abs_val)
    return qt_pattern
