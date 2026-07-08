"""DogLISP REPL: wraps reader, evaluator, and CAD builtins for interactive use."""
from pathlib import Path
from src.scripting.reader import read, tokenize
from src.scripting.eval import make_global_env, eval_expr
from src.scripting.builtins import register_cad_builtins


def _find_expr_end(source: str) -> int:
    """Find the end position of the first complete s-expression in source.
    Returns end index (exclusive) or -1 if unclosed."""
    depth = 0
    in_string = False
    started = False
    for i, ch in enumerate(source):
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == '(':
            depth += 1
            started = True
        elif ch == ')':
            depth -= 1
        elif not started and ch not in ' \t\n\r;':
            # Bare atom — ends at next whitespace or paren
            j = i
            while j < len(source) and source[j] not in ' \t\n\r();':
                j += 1
            return j
        if started and depth == 0:
            return i + 1
    return -1 if started else 0


class Repl:
    """Interactive Lisp interpreter with CAD document integration."""

    def __init__(self, document, view=None):
        self.doc = document
        self.view = view
        self.env = make_global_env()
        register_cad_builtins(self.env, self.doc)
        self._output: list[str] = []

    def eval_text(self, text: str) -> str:
        """Evaluate a single Lisp expression and return its string representation."""
        text = text.strip()
        if not text or text.startswith(';'):
            return ""
        try:
            ast = read(text)
            result = eval_expr(ast, self.env)
            return self._format_result(result)
        except SyntaxError as e:
            return f"Syntax Error: {e}"
        except NameError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    def load_file(self, filepath: str) -> list[str]:
        """Execute a .lsp file, return list of result strings."""
        path = Path(filepath)
        if not path.exists():
            return [f"File not found: {filepath}"]

        source = path.read_text()
        results = []

        remaining = source
        while remaining.strip():
            remaining = remaining.strip()
            if remaining.startswith(';'):
                nl = remaining.find('\n')
                remaining = remaining[nl + 1:] if nl >= 0 else ""
                continue
            try:
                # Find the end of the first expression by counting parens
                end = _find_expr_end(remaining)
                if end < 0:
                    results.append("Syntax Error: unclosed expression")
                    break
                expr_text = remaining[:end]
                ast = read(expr_text)
                result = eval_expr(ast, self.env)
                results.append(self._format_result(result))
                remaining = remaining[end:]
            except SyntaxError as e:
                results.append(f"Syntax Error: {e}")
                break
            except Exception as e:
                results.append(f"Error: {type(e).__name__}: {e}")
                break

        return results

    @staticmethod
    def _format_result(value) -> str:
        """Convert a Lisp value to display string."""
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "t" if value else "nil"
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            return f"{value:.6g}"
        if isinstance(value, list):
            items = " ".join(Repl._format_result(v) for v in value)
            return f"({items})"
        if hasattr(value, '__repr__'):
            # Exclude angle-bracket reprs like <builtin:...> or <lambda ...>
            r = repr(value)
            if r.startswith('<'):
                return str(value)
            return r
        return str(value)
