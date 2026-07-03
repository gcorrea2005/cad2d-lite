from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.base import Point
from src.controller.commands.modify_entity import ModifyEntityCommand


def test_modify_entity_execute_and_undo():
    doc = Document()
    line = Line(Point(0, 0), Point(10, 10))
    doc.add_entity(line)

    old_dict = line.to_dict()
    # Manually modify
    line.start = Point(5, 5)
    line.end = Point(15, 15)
    new_dict = line.to_dict()

    cmd = ModifyEntityCommand(line, old_dict, new_dict)
    doc.execute(cmd)

    assert line.start == Point(5, 5)
    assert line.end == Point(15, 15)

    doc.undo()
    assert line.start == Point(0, 0)
    assert line.end == Point(10, 10)

    doc.redo()
    assert line.start == Point(5, 5)
    assert line.end == Point(15, 15)
