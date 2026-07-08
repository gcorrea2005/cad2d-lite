"""Tests for src.scripting.eval — the DogLISP interpreter."""
import pytest
import math
from src.scripting.reader import read
from src.scripting.eval import eval_expr, Env, make_global_env


@pytest.fixture
def env():
    return make_global_env()


class TestAtoms:
    def test_integer(self, env):
        assert eval_expr(read("42"), env) == 42

    def test_float(self, env):
        assert eval_expr(read("3.14"), env) == 3.14

    def test_string(self, env):
        assert eval_expr(read('"hello"'), env) == "hello"

    def test_nil(self, env):
        assert eval_expr(read("nil"), env) is None


class TestMathBuiltins:
    def test_add(self, env):
        assert eval_expr(read("(+ 1 2)"), env) == 3
        assert eval_expr(read("(+ 1 2 3 4)"), env) == 10

    def test_sub(self, env):
        assert eval_expr(read("(- 10 3)"), env) == 7
        assert eval_expr(read("(- 5)"), env) == -5

    def test_mul(self, env):
        assert eval_expr(read("(* 2 3)"), env) == 6
        assert eval_expr(read("(* 2 3 4)"), env) == 24

    def test_div(self, env):
        assert eval_expr(read("(/ 10 2)"), env) == 5

    def test_nested_math(self, env):
        result = eval_expr(read("(+ (* 2 3) (/ 10 2))"), env)
        assert result == 11

    def test_sin_cos(self, env):
        assert eval_expr(read("(sin 0)"), env) == pytest.approx(0.0)
        assert eval_expr(read("(cos 0)"), env) == pytest.approx(1.0)

    def test_sqrt(self, env):
        assert eval_expr(read("(sqrt 16)"), env) == 4.0


class TestSpecialForms:
    def test_quote(self, env):
        result = eval_expr(read("(quote a)"), env)
        assert isinstance(result, object)
        assert hasattr(result, 'value')
        assert result.value == "a"

    def test_if_true(self, env):
        assert eval_expr(read("(if 1 10 20)"), env) == 10

    def test_if_false(self, env):
        assert eval_expr(read("(if nil 10 20)"), env) == 20

    def test_if_no_else(self, env):
        assert eval_expr(read("(if nil 10)"), env) is None

    def test_progn(self, env):
        assert eval_expr(read("(progn 1 2 3)"), env) == 3

    def test_setq(self, env):
        eval_expr(read("(setq x 42)"), env)
        assert env.get("x") == 42
        assert eval_expr(read("x"), env) == 42

    def test_defun_and_call(self, env):
        eval_expr(read("(defun square (x) (* x x))"), env)
        result = eval_expr(read("(square 5)"), env)
        assert result == 25

    def test_lambda(self, env):
        result = eval_expr(read("((lambda (x) (* x x)) 6)"), env)
        assert result == 36

    def test_let(self, env):
        result = eval_expr(read("(let ((x 3) (y 4)) (+ x y))"), env)
        assert result == 7
        # x should not leak outside let
        with pytest.raises(NameError, match="Undefined"):
            env.get("x")

    def test_defun_multiple_body(self, env):
        eval_expr(read("(defun f (x) (setq y 10) (+ x y))"), env)
        assert eval_expr(read("(f 5)"), env) == 15

    def test_recursion(self, env):
        src = """
        (defun fact (n)
          (if (<= n 1)
              1
              (* n (fact (- n 1)))))
        """
        eval_expr(read(src), env)
        assert eval_expr(read("(fact 5)"), env) == 120


class TestEvalEdgeCases:
    def test_unknown_symbol(self, env):
        with pytest.raises(NameError, match="Undefined"):
            eval_expr(read("foobar"), env)

    def test_call_non_function(self, env):
        with pytest.raises(TypeError, match="not callable"):
            eval_expr(read("(42 1)"), env)
