"""Tests for the DogLISP REPL wrapper."""
import pytest
from src.model.document import Document
from src.scripting.repl import Repl


class TestRepl:
    @pytest.fixture
    def repl(self):
        doc = Document()
        return Repl(doc)

    def test_simple_eval(self, repl):
        assert repl.eval_text("(+ 1 2)") == "3"

    def test_defun_and_call(self, repl):
        repl.eval_text("(defun double (x) (* x 2))")
        assert repl.eval_text("(double 21)") == "42"

    def test_line_creation(self, repl):
        result = repl.eval_text("(line (p 0 0) (p 100 0))")
        assert len(repl.doc.entities) == 1
        assert "(100" in result or "100" in result

    def test_syntax_error(self, repl):
        result = repl.eval_text("(foo")
        assert "Error" in result

    def test_load_file(self, repl, tmp_path):
        f = tmp_path / "test.lsp"
        f.write_text("(defun add2 (x) (+ x 2))\n(add2 40)\n")
        results = repl.load_file(str(f))
        assert "42" in results
