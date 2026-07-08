"""Tests for DogLISP CAD builtins — entity creation via Lisp."""
import pytest
from src.model.document import Document
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.scripting.reader import read
from src.scripting.eval import make_global_env, eval_expr
from src.scripting.builtins import register_cad_builtins


@pytest.fixture
def cad_env():
    """Environment with both math and CAD builtins."""
    env = make_global_env()
    doc = Document()
    register_cad_builtins(env, doc)
    return env, doc


class TestEntityCreation:
    def test_line(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(line (p 0 0) (p 100 0))"), env)
        assert len(doc.entities) == 1
        e = doc.entities[0]
        assert isinstance(e, Line)
        assert e.start == Point(0, 0)
        assert e.end == Point(100, 0)

    def test_circle(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(circle (p 50 50) 25)"), env)
        assert len(doc.entities) == 1
        e = doc.entities[0]
        assert isinstance(e, Circle)
        assert e.center == Point(50, 50)
        assert e.radius == 25

    def test_rectang(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(rectang (p 0 0) (p 100 50))"), env)
        assert len(doc.entities) == 1

    def test_layer_set(self, cad_env):
        env, doc = cad_env
        eval_expr(read('(layer "new" "walls")'), env)
        eval_expr(read('(layer "set" "walls")'), env)
        eval_expr(read("(line (p 0 0) (p 10 0))"), env)
        assert doc.entities[0].layer_name == "walls"

    def test_line_with_layer_kwarg(self, cad_env):
        env, doc = cad_env
        eval_expr(read('(line (p 0 0) (p 10 0) :layer "beams")'), env)
        assert doc.entities[0].layer_name == "beams"

    def test_doc_dirty_flag(self, cad_env):
        env, doc = cad_env
        assert not doc.is_dirty
        eval_expr(read("(line (p 0 0) (p 10 0))"), env)
        assert doc.is_dirty


class TestListOperations:
    def test_foreach_line(self, cad_env):
        env, doc = cad_env
        src = """
        (progn
          (line (p 0 0) (p 10 0))
          (line (p 0 5) (p 10 5))
          (line (p 0 10) (p 10 10)))
        """
        eval_expr(read(src), env)
        assert len(doc.entities) == 3

    def test_ssget_all(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(line (p 0 0) (p 10 0))"), env)
        eval_expr(read("(circle (p 50 50) 10)"), env)
        uuids = eval_expr(read("(ssget)"), env)
        assert len(uuids) == 2

    def test_car_cdr(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(setq lst (list 1 2 3))"), env)
        assert eval_expr(read("(car lst)"), env) == 1
        rest = eval_expr(read("(cdr lst)"), env)
        assert rest == [2, 3]

    def test_foreach_erase(self, cad_env):
        env, doc = cad_env
        eval_expr(read("(line (p 0 0) (p 10 0))"), env)
        eval_expr(read("(line (p 0 5) (p 10 5))"), env)
        assert len(doc.entities) == 2
        eval_expr(read("(erase \"all\")"), env)
        assert len(doc.entities) == 0
