import tempfile
from pathlib import Path
from src.model.document import Document
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from src.io.cad_file import save_document, load_document
import math


def test_save_load_roundtrip():
    doc = Document()
    doc.layer_manager.add_layer("walls", "#FF0000")
    doc.add_entity(Line(Point(0, 0), Point(10, 10), layer_name="walls"))
    doc.add_entity(Circle(Point(5, 5), 3))
    doc.add_entity(Arc(Point(2, 2), 5, 0, math.pi))
    doc.add_entity(Polyline([Point(0, 0), Point(5, 0), Point(5, 5)], closed=True))
    doc.add_entity(TextEntity(Point(1, 1), "Hello"))
    doc.add_entity(Dimension(Point(0, 0), Point(10, 0), Point(5, 2)))

    with tempfile.NamedTemporaryFile(suffix=".cadlite", delete=False) as f:
        path = Path(f.name)

    try:
        save_document(doc, path)
        doc2 = load_document(path)
        assert len(doc2.entities) == 6
        assert "walls" in doc2.layer_manager.layers
        assert doc2.layer_manager.layers["walls"].color == "#FF0000"

        # Verify entity types
        types = {e.to_dict()["type"] for e in doc2.entities}
        assert types == {"Line", "Circle", "Arc", "Polyline", "Text", "Dimension"}
    finally:
        path.unlink()


def test_save_document_clears_dirty():
    doc = Document()
    doc.add_entity(Line(Point(0, 0), Point(10, 10)))
    assert doc.is_dirty is True
    with tempfile.NamedTemporaryFile(suffix=".cadlite", delete=False) as f:
        path = Path(f.name)
    try:
        save_document(doc, path)
        assert doc.is_dirty is False
    finally:
        path.unlink()
