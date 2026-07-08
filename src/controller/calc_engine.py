"""Geometry calculator: CALC command — AutoCAD-style expression evaluator.

Syntax:  CALC END+PER/2        → pick endpoint, pick perpendicular, average
        CALC (END+MID)/2       → midpoint between endpoint and midpoint
        CALC SIN(45)*(CEN+DIST(END,PER))  → trig + distance
        CALC SQRT(256)+PI*2    → pure math

Snaps:  END, MID, CEN, INT, PER, NEA, QUA, TAN, NOD, INS
Funcs:  SIN COS TAN ASIN ACOS ATAN ATAN2 SQRT EXP LOG LN ABS
        POW MIN MAX ROUND FLOOR CEIL PI D2R R2D DIST ANG VEC
Ops:    + - * /    (vector ops + scalar)
Parens: ( ) for grouping
"""
import math as _math
from typing import Callable
from src.model.entities.base import Point
from src.model.snap import SnapEngine, SnapType


SNAP_NAME_MAP = {
    "END": SnapType.ENDPOINT, "MID": SnapType.MIDPOINT,
    "CEN": SnapType.CENTER,   "INT": SnapType.INTERSECTION,
    "PER": SnapType.PERPENDICULAR, "NEA": SnapType.NEAREST,
    "QUA": SnapType.QUADRANT, "TAN": SnapType.TANGENT,
    "NOD": SnapType.NODE,     "INS": SnapType.INSERTION,
}


class CalcEngine:
    """Parses and evaluates CALC expressions with interactive snapping."""

    def __init__(self, snap_engine: SnapEngine, document):
        self.snap = snap_engine
        self.doc = document
        self._pick_fn: Callable | None = None
        self._pi = _math.pi

    # ── Public API ────────────────────────────────────────────

    def eval_text(self, text: str, pick_fn: Callable[[str], Point | None]) -> Point | None:
        self._pick_fn = pick_fn
        tokens = self._tokenize(text)
        t = self._expr(tokens, 0)
        if t is None:
            return None
        return t[0]

    def snap_at(self, scene_pos: Point, snap_name: str) -> Point | None:
        st = SNAP_NAME_MAP.get(snap_name.upper())
        if st is None:
            return scene_pos
        result = self.snap.find_snap(scene_pos, self.doc.entities, {st})
        if result:
            return result.point
        return scene_pos

    # ── Tokenizer ─────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        for ch in "+-*/()[],":
            text = text.replace(ch, f" {ch} ")
        tokens = text.upper().split()
        merged = []
        i = 0
        while i < len(tokens):
            if tokens[i] == "[":
                j = i + 1
                parts = []
                while j < len(tokens) and tokens[j] != "]":
                    if tokens[j] != ",":
                        parts.append(tokens[j])
                    j += 1
                merged.append(f"[{','.join(parts)}]")
                i = j + 1
            else:
                merged.append(tokens[i])
                i += 1
        return merged

    # ── Math function dispatch ────────────────────────────────

    def _call_func(self, name: str, args: list) -> Point | None:
        """Evaluate a built-in math function. args = list of Point/number."""
        a0 = args[0] if len(args) > 0 else Point(0, 0)

        # Extract scalar from first arg
        def s(p):
            return p if isinstance(p, (int, float)) else (p.x if isinstance(p, Point) else 0.0)

        name = name.upper()

        if name == "PI":       return Point(self._pi, self._pi)
        if name == "ABS":      v = abs(s(a0)); return Point(v, v)
        if name == "ROUND":    v = round(s(a0)); return Point(v, v)
        if name == "FLOOR":    v = _math.floor(s(a0)); return Point(v, v)
        if name == "CEIL":     v = _math.ceil(s(a0)); return Point(v, v)
        if name == "SQRT":     v = _math.sqrt(s(a0)); return Point(v, v)
        if name == "EXP":      v = _math.exp(s(a0)); return Point(v, v)
        if name == "LN":       v = _math.log(s(a0)); return Point(v, v)
        if name == "LOG":      v = _math.log10(s(a0)); return Point(v, v)
        if name == "SIN":      v = _math.sin(_math.radians(s(a0))); return Point(v, v)
        if name == "COS":      v = _math.cos(_math.radians(s(a0))); return Point(v, v)
        if name == "TAN":      v = _math.tan(_math.radians(s(a0))); return Point(v, v)
        if name == "ASIN":     v = _math.degrees(_math.asin(s(a0))); return Point(v, v)
        if name == "ACOS":     v = _math.degrees(_math.acos(s(a0))); return Point(v, v)
        if name == "ATAN":     v = _math.degrees(_math.atan(s(a0))); return Point(v, v)
        if name == "D2R":      v = _math.radians(s(a0)); return Point(v, v)
        if name == "R2D":      v = _math.degrees(s(a0)); return Point(v, v)
        if name == "POW":
            b = s(a0)
            e = s(args[1]) if len(args) > 1 else 1
            v = b ** e; return Point(v, v)
        if name == "ATAN2":
            y = s(a0)
            x = s(args[1]) if len(args) > 1 else 0
            v = _math.degrees(_math.atan2(y, x)); return Point(v, v)
        if name == "MIN":
            vals = [s(a) for a in args]; v = min(vals); return Point(v, v)
        if name == "MAX":
            vals = [s(a) for a in args]; v = max(vals); return Point(v, v)

        # Vector functions
        if name == "DIST":
            a = a0 if isinstance(a0, Point) else Point(s(a0), s(a0))
            b = args[1] if len(args) > 1 else Point(0, 0)
            b = b if isinstance(b, Point) else Point(s(b), s(b))
            d = a.distance_to(b); return Point(d, d)
        if name == "VEC":
            a = a0 if isinstance(a0, Point) else Point(s(a0), s(a0))
            b = args[1] if len(args) > 1 else Point(0, 0)
            b = b if isinstance(b, Point) else Point(s(b), s(b))
            return Point(b.x - a.x, b.y - a.y)
        if name == "ANG":
            a = a0 if isinstance(a0, Point) else Point(s(a0), s(a0))
            b = args[1] if len(args) > 1 else Point(0, 0)
            b = b if isinstance(b, Point) else Point(s(b), s(b))
            ang = _math.degrees(_math.atan2(b.y - a.y, b.x - a.x))
            return Point(ang, ang)

        return None

    _FUNC_ARITY = {
        "PI": 0, "ABS": 1, "ROUND": 1, "FLOOR": 1, "CEIL": 1,
        "SQRT": 1, "EXP": 1, "LN": 1, "LOG": 1,
        "SIN": 1, "COS": 1, "TAN": 1,
        "ASIN": 1, "ACOS": 1, "ATAN": 1,
        "D2R": 1, "R2D": 1,
        "POW": 2, "ATAN2": 2, "DIST": 2, "VEC": 2, "ANG": 2,
        "MIN": -1, "MAX": -1,  # variadic
    }

    # ── Recursive descent parser ──────────────────────────────

    def _expr(self, tokens: list[str], pos: int):
        t = self._term(tokens, pos)
        if t is None: return None
        result, pos = t
        while pos < len(tokens) and tokens[pos] in "+-":
            op = tokens[pos]; pos += 1
            t = self._term(tokens, pos)
            if t is None: return None
            rhs, pos = t
            if op == "+":
                result = Point(result.x + rhs.x, result.y + rhs.y)
            else:
                result = Point(result.x - rhs.x, result.y - rhs.y)
        return result, pos

    def _term(self, tokens: list[str], pos: int):
        t = self._factor(tokens, pos)
        if t is None: return None
        result, pos = t
        while pos < len(tokens) and tokens[pos] in "*/":
            op = tokens[pos]; pos += 1
            t = self._factor(tokens, pos)
            if t is None: return None
            rhs, pos = t

            def _s(v): return v if isinstance(v, (int, float)) else (v.x if isinstance(v, Point) else 0.0)

            if op == "*":
                if isinstance(result, Point) and isinstance(rhs, Point):
                    result = Point(result.x * rhs.x, result.y * rhs.y)
                else:
                    s1 = _s(result); s2 = _s(rhs)
                    result = Point(s1 * s2, s1 * s2)
            else:
                if isinstance(result, Point) and isinstance(rhs, Point):
                    result = Point(result.x / rhs.x if rhs.x else 0, result.y / rhs.y if rhs.y else 0)
                else:
                    s1 = _s(result); s2 = _s(rhs)
                    result = Point(s1 / s2 if s2 else 0, s1 / s2 if s2 else 0)
        return result, pos

    def _factor(self, tokens: list[str], pos: int):
        if pos >= len(tokens): return None
        tok = tokens[pos]

        # Parenthesized expression
        if tok == "(":
            pos += 1
            t = self._expr(tokens, pos)
            if t is None: return None
            result, pos = t
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            return result, pos

        # Vector literal: [x,y]
        if tok.startswith("[") and tok.endswith("]"):
            inner = tok[1:-1]
            parts = inner.split(",")
            if len(parts) == 2:
                return Point(float(parts[0]), float(parts[1])), pos + 1

        # Function call: FUNC ( arg , arg ... )
        if pos + 1 < len(tokens) and tokens[pos + 1] == "(" and tok in self._FUNC_ARITY:
            pos += 2  # skip name and '('
            fargs = []
            while pos < len(tokens) and tokens[pos] != ")":
                if tokens[pos] == ",":
                    pos += 1
                    continue
                t = self._expr(tokens, pos)
                if t is None: return None
                arg, pos = t
                fargs.append(arg)
                # If next is comma or ), continue; if expression, stop
                if pos < len(tokens) and tokens[pos] == ",":
                    continue
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            r = self._call_func(tok, fargs)
            if r is None: return None
            return r, pos

        # Unary minus
        if tok == "-":
            t = self._factor(tokens, pos + 1)
            if t is None: return None
            v, npos = t
            if isinstance(v, Point):
                return Point(-v.x, -v.y), npos
            return Point(-float(v), -float(v)), npos

        # Unary plus (no-op)
        if tok == "+":
            return self._factor(tokens, pos + 1)

        # Number
        try:
            return Point(float(tok), float(tok)), pos + 1
        except ValueError:
            pass

        # Zero-arity function as bare token (PI, etc.)
        if tok in self._FUNC_ARITY and self._FUNC_ARITY[tok] == 0:
            r = self._call_func(tok, [])
            if r is not None:
                return r, pos + 1

        # Snap name
        if tok in SNAP_NAME_MAP:
            pt = self._pick_fn(tok) if self._pick_fn else None
            if pt is None: return None
            return pt, pos + 1

        return None
