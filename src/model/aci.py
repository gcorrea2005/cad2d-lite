"""
AutoCAD Color Index (ACI) — 256-color palette mapping to RGB.

Usage:
    from src.model.aci import aci_to_rgb, aci_to_hex, rgb_to_aci, COLOR_NAMES
    aci_to_rgb(1)   → (255, 0, 0)    # Red
    aci_to_hex(3)   → "#00FF00"      # Green
    rgb_to_aci(255, 0, 0) → 1        # nearest ACI match
"""

# ── Standard 9 colors ────────────────────────────────────────
_STANDARD = {
    0:  (0, 0, 0),       # BYBLOCK
    1:  (255, 0, 0),     # Red
    2:  (255, 255, 0),   # Yellow
    3:  (0, 255, 0),     # Green
    4:  (0, 255, 255),   # Cyan
    5:  (0, 0, 255),     # Blue
    6:  (255, 0, 255),   # Magenta
    7:  (255, 255, 255), # White
    8:  (65, 65, 65),    # Dark Gray
    9:  (190, 190, 190), # Light Gray
}

COLOR_NAMES = {
    1: "Red", 2: "Yellow", 3: "Green", 4: "Cyan",
    5: "Blue", 6: "Magenta", 7: "White", 8: "Dark Gray", 9: "Light Gray",
}


def _build_aci_table() -> dict[int, tuple[int, int, int]]:
    """Build full 256-color ACI → RGB table."""
    table = dict(_STANDARD)

    # Colors 10-249: hue-based
    # Hue: 0-215 in steps of 15 (0, 15, 30, ..., 345) → 24 hues
    # For each hue pair: saturation/value combos
    idx = 10
    for hue_group in range(12):  # 12 pairs of hues (even/odd hue)
        # 10 colors per hue pair
        sat_values = [
            (0.50, 1.00), (0.75, 1.00), (1.00, 0.75), (0.50, 0.75),
            (0.25, 0.75), (0.00, 0.75), (0.25, 0.50), (0.00, 0.50),
            (0.00, 0.25), (0.00, 0.00),
        ]
        for sv_idx, (sat, val) in enumerate(sat_values):
            if idx > 249:
                break
            # Two hues per group: even hue (full sat/val combos) + odd hue (same)
            for hue_offset in (0, 1):
                if idx > 249:
                    break
                hue = (hue_group * 30 + hue_offset * 15) % 360
                if sv_idx == 9 and hue_offset == 1:
                    continue  # skip duplicate black
                rgb = _hsv_to_rgb(hue / 360, sat, val)
                table[idx] = rgb
                idx += 1

    # Colors 250-255: grayscale
    gray_levels = [50, 80, 110, 150, 200, 230]
    for i, g in enumerate(gray_levels):
        table[250 + i] = (g, g, g)

    return table


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """HSV (0-1 range) → RGB (0-255)."""
    import math
    if s == 0:
        g = int(v * 255)
        return (g, g, g)
    h *= 6
    i = int(h)
    f = h - i
    p = int(v * (1 - s) * 255)
    q = int(v * (1 - s * f) * 255)
    t_val = int(v * (1 - s * (1 - f)) * 255)
    v_int = int(v * 255)
    return {
        0: (v_int, t_val, p),
        1: (q, v_int, p),
        2: (p, v_int, t_val),
        3: (p, q, v_int),
        4: (t_val, p, v_int),
        5: (v_int, p, q),
    }[i % 6]


# ── Build the table once ─────────────────────────────────────
ACI_TABLE: dict[int, tuple[int, int, int]] = _build_aci_table()

# Reverse lookup: RGB → nearest ACI
import math as _math
_ACI_LIST = sorted(ACI_TABLE.items())


def aci_to_rgb(index: int) -> tuple[int, int, int]:
    """ACI index (0-255) → RGB tuple (0-255)."""
    if index in ACI_TABLE:
        return ACI_TABLE[index]
    return (255, 255, 255)  # fallback white


def aci_to_hex(index: int) -> str:
    """ACI index → hex color string '#RRGGBB'."""
    r, g, b = aci_to_rgb(index)
    return f"#{r:02X}{g:02X}{b:02X}"


def aci_to_qcolor(index: int):
    """ACI index → QColor."""
    from PySide6.QtGui import QColor
    r, g, b = aci_to_rgb(index)
    return QColor(r, g, b)


def rgb_to_aci(r: int, g: int, b: int) -> int:
    """Find nearest ACI index for an RGB color."""
    best, best_dist = 7, float("inf")  # default white
    for idx, (cr, cg, cb) in _ACI_LIST:
        dr, dg, db = r - cr, g - cg, b - cb
        dist = dr * dr + dg * dg + db * db
        if dist < best_dist:
            best_dist = dist
            best = idx
    return best


def hex_to_aci(hex_color: str) -> int:
    """Hex string '#RRGGBB' or 'RRGGBB' → nearest ACI index."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return rgb_to_aci(r, g, b)


def parse_color(value) -> int:
    """
    Parse a color value from SETVAR/command input.
    Accepts ACI numbers (1-255), color names (Red, Blue, etc.), or hex.
    Returns ACI index.
    """
    if isinstance(value, int):
        if 0 <= value <= 255:
            return value
        return 7
    s = str(value).strip().upper()
    # Try ACI number
    try:
        idx = int(s)
        if 0 <= idx <= 255:
            return idx
    except ValueError:
        pass
    # Try color name
    name_map = {v.upper(): k for k, v in COLOR_NAMES.items()}
    if s in name_map:
        return name_map[s]
    # Try hex
    if s.startswith("#") or all(c in "0123456789ABCDEF" for c in s):
        return hex_to_aci(s)
    return 7  # default white


def color_to_display(index: int) -> str:
    """Human-friendly representation of an ACI color."""
    if index in COLOR_NAMES:
        return f"{index} ({COLOR_NAMES[index]})"
    r, g, b = aci_to_rgb(index)
    return f"{index} (#{r:02X}{g:02X}{b:02X})"
