"""
Minimal DXF writer for DWG export bridge.

ezdxf's export_dxf produces a full R2010 DXF with MATERIAL, MLEADERSTYLE,
and extended objects that LibreDWG's dxf2dwg can't handle. This module
writes a bare-bones DXF file containing only the ENTITIES section — enough
for geometry exchange without the problematic metadata.
"""

from pathlib import Path
from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.base import Point


def export_minimal_dxf(doc: Document, path: Path):
    """
    Write a minimal DXF file with only ENTITIES section.
    Skips HEADER, TABLES, BLOCKS, OBJECTS — everything that
    LibreDWG can't handle from modern ezdxf output.
    """
    lines = []
    # Header — R2000
    lines.extend([
        "0", "SECTION", "2", "HEADER",
        "9", "$ACADVER", "1", "AC1015",
        "0", "ENDSEC",
    ])

    # Tables — minimal required by LibreDWG
    lines.extend([
        "0", "SECTION", "2", "TABLES",
        # LAYER table
        "0", "TABLE", "2", "LAYER", "70", "1",
        "0", "LAYER", "2", "0", "70", "0", "62", "7", "6", "CONTINUOUS",
        "0", "ENDTAB",
        # STYLE table
        "0", "TABLE", "2", "STYLE", "70", "1",
        "0", "STYLE", "2", "STANDARD", "70", "0", "40", "0.0", "41", "1.0", "50", "0.0",
        "0", "ENDTAB",
        "0", "ENDSEC",
    ])

    # Blocks — minimal required
    lines.extend([
        "0", "SECTION", "2", "BLOCKS",
        "0", "ENDSEC",
    ])

    # Entities section — geometry only
    lines.append("0")
    lines.append("SECTION")
    lines.append("2")
    lines.append("ENTITIES")

    for entity in doc.entities:
        if isinstance(entity, Line):
            lines.extend(_write_line(entity))
        elif isinstance(entity, Circle):
            lines.extend(_write_circle(entity))
        elif isinstance(entity, Arc):
            lines.extend(_write_arc(entity))
        elif isinstance(entity, Polyline):
            lines.extend(_write_polyline(entity))

    lines.append("0")
    lines.append("ENDSEC")
    lines.append("0")
    lines.append("EOF")

    with open(path, 'w') as f:
        f.write('\n'.join(lines))
        f.write('\n')


def _write_line(ent: Line) -> list[str]:
    return [
        "0", "LINE",
        "8", getattr(ent, 'layer_name', '0') or '0',
        "10", str(ent.start.x),
        "20", str(ent.start.y),
        "30", "0.0",
        "11", str(ent.end.x),
        "21", str(ent.end.y),
        "31", "0.0",
    ]


def _write_circle(ent: Circle) -> list[str]:
    return [
        "0", "CIRCLE",
        "8", getattr(ent, 'layer_name', '0') or '0',
        "10", str(ent.center.x),
        "20", str(ent.center.y),
        "30", "0.0",
        "40", str(ent.radius),
    ]


def _write_arc(ent: Arc) -> list[str]:
    import math
    return [
        "0", "ARC",
        "8", getattr(ent, 'layer_name', '0') or '0',
        "10", str(ent.center.x),
        "20", str(ent.center.y),
        "30", "0.0",
        "40", str(ent.radius),
        "50", str(math.degrees(ent.start_angle)),
        "51", str(math.degrees(ent.end_angle)),
    ]


def _write_polyline(ent: Polyline) -> list[str]:
    result = [
        "0", "POLYLINE",
        "8", getattr(ent, 'layer_name', '0') or '0',
        "66", "1",  # vertices follow
        "70", "1" if ent.is_closed else "0",
    ]
    for pt in ent.vertices:
        result.extend([
            "0", "VERTEX",
            "8", getattr(ent, 'layer_name', '0') or '0',
            "10", str(pt.x),
            "20", str(pt.y),
            "30", "0.0",
        ])
    result.extend(["0", "SEQEND"])
    return result
