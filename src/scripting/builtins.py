"""DogLISP CAD builtins — entity creation, selection, system variables."""
import math
from typing import Any, Callable
from src.scripting.eval import Env, Builtin
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.point_entity import PointEntity


def register_cad_builtins(env: Env, document) -> None:
    """Register all CAD-specific functions into the Lisp environment."""
    doc = document

    # Current layer tracker (mutable cell shared across closures)
    _current_layer = ["0"]

    def _get_layer(kwargs: dict | None = None) -> str:
        if kwargs and "layer" in kwargs:
            return kwargs["layer"]
        return _current_layer[0]

    # ── Point constructor ──
    def make_point(x, y):
        return Point(float(x), float(y))

    def point_x(pt: Point) -> float:
        return pt.x

    def point_y(pt: Point) -> float:
        return pt.y

    env.define("p", Builtin(make_point, "p"))
    env.define("p-x", Builtin(point_x, "p-x"))
    env.define("p-y", Builtin(point_y, "p-y"))

    # ── Entity constructors ──

    def cmd_line(p1: Point, p2: Point, **kwargs):
        layer = _get_layer(kwargs)
        doc.add_entity(Line(p1, p2, layer_name=layer))
        return p2

    def cmd_circle(center: Point, radius: float, **kwargs):
        layer = _get_layer(kwargs)
        doc.add_entity(Circle(center, float(radius), layer_name=layer))
        return center

    def cmd_arc(center: Point, radius: float, start_deg: float, end_deg: float, **kwargs):
        layer = _get_layer(kwargs)
        sa = math.radians(float(start_deg))
        ea = math.radians(float(end_deg))
        doc.add_entity(Arc(center, float(radius), sa, ea, layer_name=layer))
        return center

    def cmd_rectang(p1: Point, p2: Point, **kwargs):
        layer = _get_layer(kwargs)
        vertices = [
            Point(p1.x, p1.y), Point(p2.x, p1.y),
            Point(p2.x, p2.y), Point(p1.x, p2.y),
        ]
        doc.add_entity(Polyline(vertices, closed=True, layer_name=layer))
        return p2

    def cmd_pline(*args, **kwargs):
        """(pline (p 0 0) (p 10 0) (p 10 10) :closed t)"""
        layer = _get_layer(kwargs)
        closed = kwargs.get(":closed", False)
        vertices = [a for a in args if isinstance(a, Point)]
        if len(vertices) >= 2:
            doc.add_entity(Polyline(vertices, closed=closed, layer_name=layer))
            return vertices[-1]
        return None

    def cmd_text(pt: Point, content: str, **kwargs):
        layer = _get_layer(kwargs)
        doc.add_entity(TextEntity(pt, str(content), layer_name=layer))
        return pt

    def cmd_point(pt: Point, **kwargs):
        layer = _get_layer(kwargs)
        doc.add_entity(PointEntity(pt, layer_name=layer))
        return pt

    env.define("line", Builtin(cmd_line, "line"))
    env.define("circle", Builtin(cmd_circle, "circle"))
    env.define("arc", Builtin(cmd_arc, "arc"))
    env.define("rectang", Builtin(cmd_rectang, "rectang"))
    env.define("pline", Builtin(cmd_pline, "pline"))
    env.define("text", Builtin(cmd_text, "text"))
    env.define("point", Builtin(cmd_point, "point"))

    # ── Layer commands ──
    def cmd_layer(action: str, name: str | None = None):
        lm = doc.layer_manager
        if action == "new" and name:
            if name not in lm.layers:
                lm.add_layer(name)
        elif action == "set" and name:
            if name in lm.layers:
                lm.set_current(name)
                _current_layer[0] = name
                doc.sysvars["CLAYER"] = name
        return name

    env.define("layer", Builtin(cmd_layer, "layer"))

    # ── Selection sets ──
    def cmd_ssget(filter_type=None):
        """Return list of entity UUIDs, optionally filtered by type."""
        uuids = []
        for ent in doc.entities:
            if filter_type is None:
                uuids.append(ent.uuid)
            elif filter_type == "line" and isinstance(ent, Line):
                uuids.append(ent.uuid)
            elif filter_type == "circle" and isinstance(ent, Circle):
                uuids.append(ent.uuid)
        return uuids

    env.define("ssget", Builtin(cmd_ssget, "ssget"))

    # ── System variables ──
    def cmd_setvar(name: str, value):
        doc.sysvars[name.upper()] = value
        return value

    def cmd_getvar(name: str):
        return doc.sysvars[name.upper()]

    env.define("setvar", Builtin(cmd_setvar, "setvar"))
    env.define("getvar", Builtin(cmd_getvar, "getvar"))

    # ── Erase ──
    def cmd_erase(uuid_or_all=None):
        if uuid_or_all is None or uuid_or_all == "all":
            for uid in list(doc._entities.keys()):
                doc.remove_entity(uid)
        else:
            doc.remove_entity(str(uuid_or_all))
        return None

    env.define("erase", Builtin(cmd_erase, "erase"))

    # ── List builtins ──
    def cmd_car(lst):
        return lst[0] if lst else None

    def cmd_cdr(lst):
        return lst[1:] if lst else None

    def cmd_cons(x, lst):
        return [x] + (lst if isinstance(lst, list) else [])

    def cmd_list(*args):
        return list(args)

    def cmd_length(lst):
        return len(lst) if isinstance(lst, list) else 0

    env.define("car", Builtin(cmd_car, "car"))
    env.define("cdr", Builtin(cmd_cdr, "cdr"))
    env.define("cons", Builtin(cmd_cons, "cons"))
    env.define("list", Builtin(cmd_list, "list"))
    env.define("length", Builtin(cmd_length, "length"))

    # ── Comparison (in case not in math env) ──
    env.define("=", Builtin(lambda a, b: a == b, "="))
    env.define("<", Builtin(lambda a, b: a < b, "<"))
    env.define(">", Builtin(lambda a, b: a > b, ">"))

    # ── Higher-order control flow ──
    def cmd_foreach(lst, fn):
        for item in lst:
            fn(item)
        return None

    env.define("foreach", Builtin(cmd_foreach, "foreach"))

    def cmd_repeat(n, fn):
        result = None
        for _ in range(int(n)):
            result = fn()
        return result

    env.define("repeat*", Builtin(cmd_repeat, "repeat*"))

    # ── Print / debug ──
    env.define("print", Builtin(lambda *xs: print(*xs), "print"))

    # ── Entity property access ──
    def cmd_entget(uuid_or_ent):
        """Return association list of entity properties (AutoCAD-style).
        Accepts UUID string or entity object."""
        ent = uuid_or_ent
        if isinstance(ent, str):
            ent = doc._entities.get(ent)
        if ent is None:
            return None

        t = type(ent).__name__
        alist = [
            ("type", t),
            ("uuid", ent.uuid),
            ("layer", ent.layer_name),
            ("color", ent.color),
            ("linetype", ent.linetype),
        ]

        if t == "Line":
            alist += [
                ("start", (ent.start.x, ent.start.y)),
                ("end",   (ent.end.x,   ent.end.y)),
            ]
        elif t == "Circle":
            alist += [
                ("center", (ent.center.x, ent.center.y)),
                ("radius", ent.radius),
            ]
        elif t == "Arc":
            alist += [
                ("center",      (ent.center.x, ent.center.y)),
                ("radius",      ent.radius),
                ("start_angle", ent.start_angle),
                ("end_angle",   ent.end_angle),
            ]
        elif t == "Polyline":
            alist += [
                ("vertices", [(v.x, v.y) for v in ent.vertices]),
                ("closed",   ent.is_closed),
            ]
        elif t == "Ellipse":
            alist += [
                ("center",      (ent.center.x, ent.center.y)),
                ("major_axis",  (ent.major_axis.x, ent.major_axis.y)),
                ("ratio",       ent.ratio),
            ]
        elif t == "TextEntity":
            alist += [
                ("position", (ent.position.x, ent.position.y)),
                ("content",  ent.content),
                ("height",   ent.height),
                ("rotation", ent.rotation),
            ]
        elif t == "PointEntity":
            alist += [
                ("position", (ent.position.x, ent.position.y)),
            ]

        return alist

    env.define("entget", Builtin(cmd_entget, "entget"))

    def cmd_entsel():
        """Return UUIDs of all entities (simplified — no interactive pick)."""
        return [ent.uuid for ent in doc.entities]

    env.define("entsel", Builtin(cmd_entsel, "entsel"))

    # ── Version ──
    env.define("ver", Builtin(lambda: "DogCAD 2D Lite v0.1.0", "ver"))

    # ── Geometry calculator ──
    def cmd_cal(expr: str):
        """Evaluate a CALC expression: (cal \"END+PER/2\"). Returns point as tuple."""
        from src.controller.calc_engine import CalcEngine
        from src.model.snap import SnapEngine
        engine = CalcEngine(SnapEngine(snap_distance=15.0), doc)
        # For Lisp, snap tokens return None → expression won't evaluate
        # unless all tokens are numeric/vector literals
        result = engine.eval_text(expr, lambda s: None)
        if result:
            return (result.x, result.y)
        return None

    env.define("cal", Builtin(cmd_cal, "cal"))

    # ── OSNAP / OSMODE ──
    def cmd_osmode(new_val=None):
        """Get or set OSMODE. (osmode) → current value, (osmode 7) → set to 7."""
        from src.model.snap import OSMODE_NAMES
        if new_val is None:
            return doc.sysvars["OSMODE"]
        if isinstance(new_val, str):
            val = 0
            for p in new_val.upper().split(","):
                p = p.strip()
                if p in OSMODE_NAMES:
                    val |= OSMODE_NAMES[p]
            doc.sysvars["OSMODE"] = val
            return val
        doc.sysvars["OSMODE"] = int(new_val)
        return int(new_val)

    env.define("osmode", Builtin(cmd_osmode, "osmode"))
