import ezdxf
from pathlib import Path
from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
import math


def export_dxf(document: Document, path: Path) -> None:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for entity in document.entities:
        layer = entity.layer_name
        if isinstance(entity, Line):
            msp.add_line(
                (entity.start.x, entity.start.y),
                (entity.end.x, entity.end.y),
                dxfattribs={"layer": layer},
            )
        elif isinstance(entity, Circle):
            msp.add_circle(
                (entity.center.x, entity.center.y),
                entity.radius,
                dxfattribs={"layer": layer},
            )
        elif isinstance(entity, Arc):
            msp.add_arc(
                (entity.center.x, entity.center.y),
                entity.radius,
                math.degrees(entity.start_angle),
                math.degrees(entity.end_angle),
                dxfattribs={"layer": layer},
            )
        elif isinstance(entity, Polyline):
            points = [(v.x, v.y) for v in entity.vertices]
            pl = msp.add_lwpolyline(points, dxfattribs={"layer": layer})
            if entity.is_closed:
                pl.closed = True
        elif isinstance(entity, TextEntity):
            msp.add_text(
                entity.content,
                dxfattribs={
                    "layer": layer,
                    "height": entity.height,
                    "insert": (entity.position.x, entity.position.y),
                },
            )
        elif isinstance(entity, Dimension):
            msp.add_aligned_dim(
                p1=(entity.def_point1.x, entity.def_point1.y),
                p2=(entity.def_point2.x, entity.def_point2.y),
                distance=entity.text_position.y - entity.def_point1.y,
                dxfattribs={"layer": layer},
            )

    for layer in document.layer_manager.layers.values():
        if layer.name != "0":
            doc.layers.add(name=layer.name)

    doc.saveas(str(path))
