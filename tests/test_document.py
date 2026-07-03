from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.base import Point


def test_document_creation():
    doc = Document()
    assert len(doc.entities) == 0
    assert doc.layer_manager.current_layer_name == "0"

def test_add_entity():
    doc = Document()
    line = Line(Point(0, 0), Point(10, 10))
    doc.add_entity(line)
    assert len(doc.entities) == 1

def test_undo_redo():
    doc = Document()
    line = Line(Point(0, 0), Point(10, 10))
    doc.add_entity(line)
    assert len(doc.entities) == 1
    doc.undo()
    assert len(doc.entities) == 0
    doc.redo()
    assert len(doc.entities) == 1

def test_remove_entity():
    doc = Document()
    line = Line(Point(0, 0), Point(10, 10))
    doc.add_entity(line)
    doc.remove_entity(line.uuid)
    assert len(doc.entities) == 0

def test_clear_redo_stack_on_new_action():
    doc = Document()
    doc.add_entity(Line(Point(0, 0), Point(10, 10)))
    doc.undo()
    doc.add_entity(Line(Point(0, 0), Point(5, 5)))
    assert len(doc.entities) == 1
    doc.redo()  # should do nothing — redo stack was cleared
    assert len(doc.entities) == 1

def test_is_dirty():
    doc = Document()
    assert doc.is_dirty is False
    doc.add_entity(Line(Point(0, 0), Point(10, 10)))
    assert doc.is_dirty is True
