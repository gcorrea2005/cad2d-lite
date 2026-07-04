"""Unit formatting — converts raw distances to display strings with units."""
from src.model.sysvars import SysVars

# LUNITS values
DECIMAL = 2
ENGINEERING = 3
ARCHITECTURAL = 4
METRIC_M = 5  # meters
METRIC_CM = 6  # centimeters  
METRIC_MM = 7  # millimeters

UNIT_LABELS = {
    DECIMAL: "",
    ENGINEERING: '"',
    ARCHITECTURAL: '"',
    METRIC_M: " m",
    METRIC_CM: " cm",
    METRIC_MM: " mm",
}


def format_distance(value: float, sysvars: SysVars) -> str:
    """Format a distance value with units."""
    try:
        lunits = int(sysvars["LUNITS"])
    except Exception:
        lunits = DECIMAL
    try:
        luprec = int(sysvars["LUPREC"])
    except Exception:
        luprec = 2

    fmt = f".{luprec}f"

    if lunits == METRIC_M:
        return f"{value:.{luprec}f} m"
    elif lunits == METRIC_CM:
        return f"{value * 100:.{luprec}f} cm"
    elif lunits == METRIC_MM:
        return f"{value * 1000:.{luprec}f} mm"
    elif lunits == ARCHITECTURAL:
        # Convert to feet-inches
        total_inches = value * 12
        feet = int(total_inches // 12)
        inches = total_inches % 12
        return f"{feet}'-{inches:.{luprec}f}\""
    else:
        return f"{value:.{luprec}f}"


def get_unit_label(sysvars: SysVars) -> str:
    """Get short unit label for status bar."""
    try:
        lunits = int(sysvars["LUNITS"])
    except Exception:
        lunits = DECIMAL
    return UNIT_LABELS.get(lunits, "")


def set_units(sysvars: SysVars, lunits: int, luprec: int = 2) -> str:
    """Set drawing units. Returns description string."""
    names = {
        DECIMAL: "Decimal",
        ENGINEERING: "Engineering",
        ARCHITECTURAL: "Architectural",
        METRIC_M: "Metric (meters)",
        METRIC_CM: "Metric (centimeters)",
        METRIC_MM: "Metric (millimeters)",
    }
    sysvars["LUNITS"] = lunits
    sysvars["LUPREC"] = luprec
    return f"{names.get(lunits, '?')}, {luprec} decimals"
