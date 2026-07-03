from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.base import Point
from src.io.dxf_export import export_dxf
from pathlib import Path
import tempfile


def test_export_dxf():
    doc = Document()
    doc.add_entity(Line(Point(0, 0), Point(10, 10)))
    doc.add_entity(Circle(Point(5, 5), 5))

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
        path = Path(f.name)

    try:
        export_dxf(doc, path)
        content = path.read_text()
        assert "LINE" in content
        assert "CIRCLE" in content
        assert "ENTITIES" in content
    finally:
        path.unlink()
