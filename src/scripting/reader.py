"""DogLISP reader: lexer (tokenize) + parser (parse/read)."""
from dataclasses import dataclass
from typing import Any, Union


@dataclass(frozen=True, slots=True)
class Atom:
    """A leaf value in the AST: number, symbol, string, or nil."""
    value: Any
    type: str = "symbol"  # "symbol" | "integer" | "float" | "string" | "nil"

    def __eq__(self, other):
        if isinstance(other, Atom):
            return self.value == other.value and self.type == other.type
        return False

    def __hash__(self):
        return hash((self.value, self.type))

    def __repr__(self):
        if self.type == "string":
            return f'"{self.value}"'
        if self.type == "nil":
            return "nil"
        return str(self.value)


SExpr = Union[Atom, list]  # an s-expression is an atom or a list of s-expressions


def tokenize(source: str) -> list[str]:
    """Break source text into tokens. Handles parens, strings, comments, quote."""
    tokens = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]

        # Skip whitespace
        if ch in ' \t\n\r':
            i += 1
            continue

        # Skip line comments
        if ch == ';':
            while i < n and source[i] != '\n':
                i += 1
            continue

        # Parentheses
        if ch in '()':
            tokens.append(ch)
            i += 1
            continue

        # Quote shorthand: 'x -> (quote x)
        if ch == "'":
            tokens.append("'")
            i += 1
            continue

        # String literals
        if ch == '"':
            j = i + 1
            while j < n and source[j] != '"':
                if source[j] == '\\':
                    j += 1  # skip escaped char
                j += 1
            tokens.append(source[i:j+1])
            i = j + 1
            continue

        # Atoms (symbols, numbers)
        j = i
        while j < n and source[j] not in ' \t\n\r();"':
            j += 1
        tokens.append(source[i:j])
        i = j

    return tokens


def _parse_tokens(tokens: list[str], pos: int = 0) -> tuple[SExpr, int]:
    """Recursive descent: parse one expression starting at pos. Returns (expr, next_pos)."""
    if pos >= len(tokens):
        raise SyntaxError("Unexpected end of input")

    token = tokens[pos]

    # List: ( ... )
    if token == '(':
        pos += 1
        items = []
        while pos < len(tokens) and tokens[pos] != ')':
            item, pos = _parse_tokens(tokens, pos)
            items.append(item)
        if pos >= len(tokens):
            raise SyntaxError("Unclosed parenthesis")
        return items, pos + 1  # skip ')'

    # Closing paren with no opener
    if token == ')':
        raise SyntaxError("Unexpected ')'")

    # Quote shorthand: 'x -> (quote x)
    if token == "'":
        quoted, pos = _parse_tokens(tokens, pos + 1)
        return [Atom("quote", "symbol"), quoted], pos

    # String literal
    if token.startswith('"') and token.endswith('"'):
        inner = token[1:-1]
        # Unescape basic escapes
        inner = inner.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
        return Atom(inner, "string"), pos + 1

    # Number
    if _looks_like_number(token):
        return Atom(_parse_number(token), _number_type(token)), pos + 1

    # nil
    if token == 'nil':
        return Atom(None, "nil"), pos + 1

    # Symbol
    return Atom(token, "symbol"), pos + 1


def _looks_like_number(s: str) -> bool:
    """Check if token can be parsed as integer or float."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def _parse_number(s: str) -> int | float:
    """Parse numeric token, preferring int when possible."""
    if '.' in s or 'e' in s.lower():
        return float(s)
    return int(s)


def _number_type(s: str) -> str:
    if '.' in s or 'e' in s.lower():
        return "float"
    return "integer"


def parse(tokens: list[str]) -> SExpr:
    """Parse token list into an AST (nested Python lists + Atoms)."""
    if not tokens:
        raise SyntaxError("Empty input")
    expr, pos = _parse_tokens(tokens, 0)
    return expr


def read(source: str) -> SExpr:
    """One-shot: text -> AST. Returns the first expression."""
    return parse(tokenize(source))
