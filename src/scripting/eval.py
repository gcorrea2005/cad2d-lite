"""DogLISP evaluator: recursive tree-walk interpreter.

Core concepts:
  - Env: linked-list of frames for scoping (supports dynamic scoping)
  - Lambda: user-defined function closure
  - Builtin: Python callable wrapped for Lisp
  - eval_expr: recursive AST walker with special form handling
"""
import math as _math
from typing import Any, Callable
from src.scripting.reader import Atom, SExpr


# ── Environment ─────────────────────────────────────────────────

class Env:
    """A linked-list of frames: each frame maps name -> value. Inner frames shadow outer."""

    def __init__(self, parent: "Env | None" = None):
        self._bindings: dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any) -> None:
        self._bindings[name] = value

    def set(self, name: str, value: Any) -> None:
        """Set in the nearest frame that has the name, or current if not found."""
        if name in self._bindings:
            self._bindings[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            self._bindings[name] = value

    def get(self, name: str) -> Any:
        if name in self._bindings:
            return self._bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined symbol: {name}")


# ── Callable types ──────────────────────────────────────────────

class Lambda:
    """User-defined function: closure over params + body + env."""

    def __init__(self, params: list[str], body: SExpr, env: Env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        call_env = Env(parent=self.env)
        if len(args) != len(self.params):
            raise TypeError(
                f"{len(self.params)} args expected, got {len(args)}"
            )
        for name, val in zip(self.params, args):
            call_env.define(name, val)
        return eval_expr(self.body, call_env)

    def __repr__(self):
        return f"<lambda ({' '.join(self.params)})>"


class Builtin:
    """A Python function callable from Lisp."""

    def __init__(self, fn: Callable, name: str = ""):
        self.fn = fn
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def __repr__(self):
        return f"<builtin:{self.name}>"


# ── Evaluator ───────────────────────────────────────────────────

def eval_expr(expr: SExpr, env: Env) -> Any:
    """Evaluate an s-expression in the given environment."""

    # ── Atom ──
    if isinstance(expr, Atom):
        if expr.type in ("integer", "float", "string"):
            return expr.value
        if expr.type == "nil" or expr.value is None:
            return None
        # Symbol lookup — keywords (:foo) are self-evaluating
        if expr.value.startswith(":"):
            return expr.value
        return env.get(expr.value)

    # ── Empty list ──
    if not isinstance(expr, list):
        return expr
    if not expr:
        return None

    first = expr[0]
    rest = expr[1:]

    # ── Special forms ──

    # (quote x)
    if _is_symbol(first, "quote"):
        if len(rest) != 1:
            raise SyntaxError("quote requires exactly 1 argument")
        return rest[0]

    # (if test then [else])
    if _is_symbol(first, "if"):
        test_val = eval_expr(rest[0], env)
        if test_val is not None and test_val is not False:
            return eval_expr(rest[1], env)
        if len(rest) >= 3:
            return eval_expr(rest[2], env)
        return None

    # (progn expr*)
    if _is_symbol(first, "progn"):
        return _eval_progn(rest, env)

    # (setq name value)
    if _is_symbol(first, "setq"):
        name_atom = rest[0]
        if not isinstance(name_atom, Atom) or name_atom.type != "symbol":
            raise SyntaxError("setq: first argument must be a symbol")
        val = eval_expr(rest[1], env)
        env.set(name_atom.value, val)
        return val

    # (defun name (params) body...)
    if _is_symbol(first, "defun"):
        name_atom = rest[0]
        param_list = rest[1]
        params = [p.value for p in param_list if isinstance(p, Atom)]
        body = rest[2] if len(rest) == 3 else [Atom("progn", "symbol")] + list(rest[2:])
        fn = Lambda(params, body, env)
        env.define(name_atom.value, fn)
        return fn

    # (lambda (params) body...)
    if _is_symbol(first, "lambda"):
        param_list = rest[0]
        params = [p.value for p in param_list if isinstance(p, Atom)]
        body = rest[1] if len(rest) == 2 else [Atom("progn", "symbol")] + list(rest[1:])
        return Lambda(params, body, env)

    # (let ((var val) ...) body...)
    if _is_symbol(first, "let"):
        bindings = rest[0]
        let_env = Env(parent=env)
        for binding in bindings:
            if isinstance(binding, list) and len(binding) == 2:
                var_name = binding[0].value if isinstance(binding[0], Atom) else binding[0]
                var_val = eval_expr(binding[1], env)
                let_env.define(var_name, var_val)
        if len(rest) == 2:
            return eval_expr(rest[1], let_env)
        body = [Atom("progn", "symbol")] + list(rest[1:])
        return eval_expr(body, let_env)

    # ── Function call ──
    fn = eval_expr(first, env)
    raw_args = [eval_expr(a, env) for a in rest]

    # Extract keyword pairs: (:key val) -> kwargs
    args = []
    kwargs = {}
    i = 0
    while i < len(raw_args):
        if isinstance(raw_args[i], str) and raw_args[i].startswith(":") and i + 1 < len(raw_args):
            key = raw_args[i][1:]  # strip leading ":"
            kwargs[key] = raw_args[i + 1]
            i += 2
        else:
            args.append(raw_args[i])
            i += 1

    if callable(fn):
        return fn(*args, **kwargs)

    raise TypeError(f"'{first}' is not callable")


def _eval_progn(exprs: list, env: Env) -> Any:
    """Evaluate a sequence, return the last value."""
    result = None
    for e in exprs:
        result = eval_expr(e, env)
    return result


def _is_symbol(atom: Atom | object, name: str) -> bool:
    """Check if an atom is a symbol with the given name."""
    return isinstance(atom, Atom) and atom.type == "symbol" and atom.value == name


# ── Global environment ──────────────────────────────────────────

def make_global_env() -> Env:
    """Create the top-level environment with built-in functions."""
    env = Env()

    math_fns = {
        "+": lambda *xs: sum(xs),
        "-": lambda x, *xs: -x if not xs else x - sum(xs),
        "*": lambda *xs: 1 if not xs else (xs[0] if len(xs) == 1 else xs[0] * _math.prod(xs[1:])),
        "/": lambda x, y: x / y,
        "sin": _math.sin,
        "cos": _math.cos,
        "tan": _math.tan,
        "sqrt": _math.sqrt,
        "abs": abs,
        "max": max,
        "min": min,
        "expt": pow,
        "mod": lambda a, b: a % b,
        "pi": _math.pi,
        "<": lambda a, b: a < b,
        ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b,
        "=": lambda a, b: a == b,
    }
    for name, fn in math_fns.items():
        env.define(name, Builtin(fn, name))

    # Type predicates
    env.define("number?", Builtin(lambda x: isinstance(x, (int, float)), "number?"))
    env.define("list?", Builtin(lambda x: isinstance(x, list), "list?"))

    # T constant
    env.define("t", True)

    return env
