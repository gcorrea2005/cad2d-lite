import json
from pathlib import Path
from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from src.model.entities.point_entity import PointEntity
from src.model.entities.block import BlockInstance
from src.model.entities.ellipse import Ellipse

ENTITY_CLASSES = {
    "Line": Line,
    "Circle": Circle,
    "Arc": Arc,
    "Polyline": Polyline,
    "Text": TextEntity,
    "Dimension": Dimension,
    "Point": PointEntity,
    "BlockInstance": BlockInstance,
    "Ellipse": Ellipse,
}


def save_document(doc: Document, path: Path) -> None:
    data = {
        "version": 1,
        "layers": doc.layer_manager.to_dict(),
        "entities": [e.to_dict() for e in doc.entities],
    }
    path.write_text(json.dumps(data, indent=2))
    doc._dirty = False


def load_document(path: Path) -> Document:
    data = json.loads(path.read_text())
    doc = Document(filename=str(path))
    doc.layer_manager = doc.layer_manager.from_dict(data.get("layers", {}))
    for edata in data.get("entities", []):
        cls = ENTITY_CLASSES.get(edata["type"])
        if cls:
            doc._entities[edata["uuid"]] = cls.from_dict(edata)
            doc._entity_order.append(edata["uuid"])
    doc._dirty = False
    return doc
