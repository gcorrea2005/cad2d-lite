"""
System variables (SETVAR) — AutoCAD R10-style registry.

Usage:
    from src.model.sysvars import SysVars
    sv = SysVars()
    sv["OSMODE"]         # read
    sv["OSMODE"] = 35    # write (validates + syncs)
    sv.setvar("OSMODE")  # command-style: returns (value, readonly) tuple
"""

from typing import Any


# ── OSMODE bitmask ─────────────────────────────────────────────
OSMODE_BITS = {
    "END": 1, "MID": 2, "CEN": 4, "NOD": 8,
    "QUA": 16, "INT": 32, "INS": 64,
    "PER": 128, "TAN": 256, "NEA": 512, "QUI": 1024,
}


class SysVar:
    __slots__ = ("default", "readonly", "vtype", "on_change")

    def __init__(self, default: Any, *, readonly: bool = False,
                 vtype=None, on_change=None):
        self.default = default
        self.readonly = readonly
        self.vtype = vtype
        self.on_change = on_change


# ── Defaults ───────────────────────────────────────────────────
_DEFAULTS: dict[str, SysVar] = {
    # Bloque A — Imprescindibles
    "OSMODE":       SysVar(0,        vtype=int),
    "APERTURE":     SysVar(10,       vtype=int),
    "PICKBOX":      SysVar(3,        vtype=int),
    "ORTHOMODE":    SysVar(0,        vtype=int),
    "COORDS":       SysVar(2,        vtype=int),
    "CLAYER":       SysVar("0",      vtype=str),
    "FILLETRAD":    SysVar(0.0,      vtype=(int, float)),
    "CHAMFERA":     SysVar(0.0,      vtype=(int, float)),
    "CHAMFERB":     SysVar(0.0,      vtype=(int, float)),
    "TEXTSIZE":     SysVar(0.2,      vtype=(int, float)),
    "OFFSETDIST":   SysVar(-1.0,     vtype=(int, float)),
    "MIRRTEXT":     SysVar(1,        vtype=int),
    # Bloque B — Dimensionado
    "DIMSCALE":     SysVar(1.0,      vtype=(int, float)),
    "DIMTXT":       SysVar(0.18,     vtype=(int, float)),
    "DIMASZ":       SysVar(0.18,     vtype=(int, float)),
    "DIMEXO":       SysVar(0.0625,   vtype=(int, float)),
    "DIMEXE":       SysVar(0.18,     vtype=(int, float)),
    "DIMDLI":       SysVar(0.38,     vtype=(int, float)),
    "DIMTAD":       SysVar(0,        vtype=int),
    "DIMZIN":       SysVar(0,        vtype=int),
    # Bloque C — Grid/Snap/Limites
    "GRIDMODE":     SysVar(0,        vtype=int),
    "GRIDUNIT":     SysVar("0,0",    vtype=str),
    "SNAPMODE":     SysVar(0,        vtype=int),
    "SNAPUNIT":     SysVar("1,1",    vtype=str),
    "LIMMIN":       SysVar("0,0",    vtype=str),
    "LIMMAX":       SysVar("12,9",   vtype=str),
    # Bloque D — Estilo de entidad
    "CECOLOR":      SysVar("BYLAYER", vtype=str),
    "CELTYPE":      SysVar("BYLAYER", vtype=str),
    "LTSCALE":      SysVar(1.0,      vtype=(int, float)),
    "FILLMODE":     SysVar(1,        vtype=int),
    # Bloque E — Unidades
    "LUNITS":       SysVar(2,        vtype=int),
    "LUPREC":       SysVar(4,        vtype=int),
    "AUNITS":       SysVar(0,        vtype=int),
    # Bloque F — Estado/Utilidad
    "BLIPMODE":     SysVar(1,        vtype=int),
    "EXPERT":       SysVar(0,        vtype=int),
    "DRAGMODE":     SysVar(2,        vtype=int),
    "CMDECHO":      SysVar(1,        vtype=int),
    # Bloque G — Read-only
    "LASTPOINT":    SysVar("0,0",    readonly=True, vtype=str),
    "LASTANGLE":    SysVar(0.0,      readonly=True, vtype=(int, float)),
    "DWGNAME":      SysVar("",       readonly=True, vtype=str),
    "ACADVER":      SysVar("R10",    readonly=True, vtype=str),

    # Point display
    "PDMODE":       SysVar(3,        vtype=int),   # 0=dot 1=none 2=cross 3=X 4=tick +32=circle +64=square
    "PDSIZE":       SysVar(0.0,      vtype=(int, float)),  # 0=5% viewport, >0=absolute
}


class SysVars:
    """In-memory system variable store with validation and persistence."""

    def __init__(self):
        self._values: dict[str, Any] = {n: sv.default for n, sv in _DEFAULTS.items()}

    def __getitem__(self, name: str) -> Any:
        return self._values[name.upper()]

    def __setitem__(self, name: str, value: Any):
        name = name.upper()
        sv = _DEFAULTS.get(name)
        if sv is None:
            raise KeyError(f"Unknown system variable: {name}")
        if sv.readonly:
            raise ValueError(f"{name} is read-only")
        value = _DEFAULTS[name]._coerce(value)
        old = self._values.get(name)
        self._values[name] = value
        if value != old and sv.on_change:
            sv.on_change(value)

    def setvar(self, name: str) -> tuple:
        """Return (value, readonly) — for 'SETVAR NAME' display."""
        name = name.upper()
        sv = _DEFAULTS.get(name)
        if sv is None:
            raise KeyError(f"Unknown system variable: {name}")
        return self._values[name], sv.readonly

    def setvar_set(self, name: str, raw: str) -> None:
        """Parse string from command line and set variable."""
        name = name.upper()
        sv = _DEFAULTS.get(name)
        if sv is None:
            raise KeyError(f"Unknown system variable: {name}")
        if sv.readonly:
            raise ValueError(f"{name} is read-only")
        self[name] = sv._parse_raw(raw)

    def list_vars(self, pattern: str = "*") -> list:
        """Return [(name, value, readonly), ...] matching wildcard."""
        import fnmatch
        pattern = pattern.upper()
        result = []
        for name in sorted(_DEFAULTS):
            if fnmatch.fnmatch(name, pattern):
                result.append((name, self._values[name], _DEFAULTS[name].readonly))
        return result

    def to_dict(self) -> dict:
        return dict(self._values)

    @classmethod
    def from_dict(cls, data: dict) -> "SysVars":
        sv = cls()
        for name, value in data.items():
            name = name.upper()
            spec = _DEFAULTS.get(name)
            if spec and not spec.readonly:
                try:
                    sv[name] = value
                except (ValueError, TypeError, KeyError):
                    pass
        return sv

    @property
    def names(self) -> list[str]:
        return sorted(_DEFAULTS.keys())


# Helper methods on SysVar for self-contained coercion
def _sysvar_coerce(self, value):
    """Coerce value to the expected type."""
    if self.vtype is not None:
        expected = self.vtype if isinstance(self.vtype, tuple) else (self.vtype,)
        if not isinstance(value, expected):
            names = ", ".join(t.__name__ for t in expected)
            raise TypeError(f"Expected {names}, got {type(value).__name__}")
    return value


def _sysvar_parse_raw(self, raw: str):
    """Parse a command-line string into typed value."""
    raw = raw.strip()
    # int/float
    if self.vtype in ((int, float), int):
        try:
            v = int(raw) if self.vtype == int else (int(raw) if "." not in raw and raw.isdigit() else float(raw))
            return v
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                raise ValueError(f"Invalid numeric value: '{raw}'")
    if self.vtype == str:
        return raw
    # compound: try int first, then float
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


SysVar._coerce = _sysvar_coerce
SysVar._parse_raw = _sysvar_parse_raw
