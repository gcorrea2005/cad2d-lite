"""Tests for src.scripting.reader — lexer + parser."""
import pytest
from src.scripting.reader import tokenize, parse, read, Atom


class TestTokenize:
    def test_empty_string(self):
        assert tokenize("") == []

    def test_single_atom(self):
        assert tokenize("hello") == ["hello"]

    def test_number(self):
        assert tokenize("42") == ["42"]
        assert tokenize("-3.14") == ["-3.14"]

    def test_parens(self):
        assert tokenize("(a b)") == ["(", "a", "b", ")"]

    def test_nested_parens(self):
        assert tokenize("(a (b c))") == ["(", "a", "(", "b", "c", ")", ")"]

    def test_string_literal(self):
        assert tokenize('"hello world"') == ['"hello world"']

    def test_quote(self):
        assert tokenize("'x") == ["'", "x"]
        assert tokenize("'(1 2)") == ["'", "(", "1", "2", ")"]

    def test_comment_ignored(self):
        assert tokenize("; this is a comment\n42") == ["42"]

    def test_mixed(self):
        src = '(defun square (x) (* x x))'
        assert tokenize(src) == [
            "(", "defun", "square", "(", "x", ")", "(", "*", "x", "x", ")", ")"
        ]

    def test_whitespace_robust(self):
        assert tokenize("  (  a   b  )  ") == ["(", "a", "b", ")"]


class TestParse:
    def test_atom_symbol(self):
        result = parse(["hello"])
        assert isinstance(result, Atom)
        assert result.value == "hello"
        assert result.type == "symbol"

    def test_atom_integer(self):
        result = parse(["42"])
        assert result.value == 42
        assert result.type == "integer"

    def test_atom_float(self):
        result = parse(["3.14"])
        assert result.value == 3.14
        assert result.type == "float"

    def test_atom_negative_float(self):
        result = parse(["-0.5"])
        assert result.value == -0.5

    def test_simple_list(self):
        result = parse(["(", "a", "b", ")"])
        assert result == [Atom("a", "symbol"), Atom("b", "symbol")]

    def test_nested_list(self):
        result = parse(["(", "a", "(", "b", "c", ")", ")"])
        assert result == [
            Atom("a", "symbol"),
            [Atom("b", "symbol"), Atom("c", "symbol")],
        ]

    def test_empty_list(self):
        assert parse(["(", ")"]) == []

    def test_quote_shorthand(self):
        result = parse(["'", "x"])
        assert result == [Atom("quote", "symbol"), Atom("x", "symbol")]

    def test_quote_list(self):
        result = parse(["'", "(", "1", "2", ")"])
        assert result == [Atom("quote", "symbol"), [Atom(1, "integer"), Atom(2, "integer")]]

    def test_string_atom(self):
        result = parse(['"hello"'])
        assert result.value == "hello"
        assert result.type == "string"

    def test_nil(self):
        result = parse(["nil"])
        assert result.value is None


class TestRead:
    """Round-trip: text → AST."""
    def test_read_atom(self):
        result = read("42")
        assert isinstance(result, Atom)
        assert result.value == 42

    def test_read_list(self):
        result = read("(+ 1 2)")
        assert result == [Atom("+", "symbol"), Atom(1, "integer"), Atom(2, "integer")]

    def test_read_nested(self):
        result = read("(defun f (x) (+ x 1))")
        assert len(result) == 4
        assert result[0] == Atom("defun", "symbol")
        assert result[1] == Atom("f", "symbol")

    def test_read_multiple_exprs(self):
        """read() returns first expr; extra tokens ignored."""
        result = read("a b")
        assert isinstance(result, Atom)
        assert result.value == "a"
