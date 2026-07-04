"""
DXF Import — read AutoCAD DXF files into DogCAD document.
Uses ezdxf for parsing.
"""
from pathlib import Path
import math
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.point_entity import PointEntity
from src.model.entities.dimension import Dimension


def import_dxf(filepath: Path, document) -> int:
    """
    Import a DXF file into the document.
    Returns the number of entities imported.
    """
    import ezdxf
    doc = ezdxf.readfile(str(filepath))
    msp = doc.modelspace()
    count = 0

    for entity in msp:
        try:
            imported = _import_entity(entity, document)
            if imported:
                count += 1
        except Exception:
            continue

    return count


def _import_entity(entity, document) -> bool:
    """Import a single ezdxf entity into DogCAD document. Returns True if imported."""
    dxftype = entity.dxftype()

    if dxftype == "LINE":
        start = Point(entity.dxf.start.x, entity.dxf.start.y)
        end = Point(entity.dxf.end.x, entity.dxf.end.y)
        document.add_entity(Line(start, end,
                                 layer_name=_layer(entity),
                                 color=str(_aci(entity))))
        return True

    elif dxftype == "CIRCLE":
        center = Point(entity.dxf.center.x, entity.dxf.center.y)
        radius = entity.dxf.radius
        document.add_entity(Circle(center, radius,
                                   layer_name=_layer(entity),
                                   color=str(_aci(entity))))
        return True

    elif dxftype == "ARC":
        center = Point(entity.dxf.center.x, entity.dxf.center.y)
        radius = entity.dxf.radius
        start_angle = math.radians(entity.dxf.start_angle)
        end_angle = math.radians(entity.dxf.end_angle)
        document.add_entity(Arc(center, radius, start_angle, end_angle,
                                layer_name=_layer(entity),
                                color=str(_aci(entity))))
        return True

    elif dxftype == "LWPOLYLINE":
        # Handle vertices, possibly with bulge (arc segments)
        pts_data = entity.get_points('xyb') if hasattr(entity, 'get_points') else entity.get_points('xy')
        if not pts_data:
            return False

        # Convert to vertices, splitting arc segments
        vertices = []
        for i, pt_data in enumerate(pts_data):
            x, y = pt_data[0], pt_data[1]
            bulge = pt_data[2] if len(pt_data) > 2 else 0.0
            if abs(bulge) > 0.0001 and i > 0 and vertices:
                # Bulge = tan(angle/4), angle = sweep of arc
                # Generate arc points between previous vertex and this one
                prev = vertices[-1]
                chord_len = math.hypot(x - prev.x, y - prev.y)
                angle = 4 * math.atan(bulge)  # total sweep angle
                radius = chord_len / (2 * abs(math.sin(angle / 2))) if abs(math.sin(angle / 2)) > 0.001 else chord_len
                # Approximate arc with line segments
                mid_x = (prev.x + x) / 2
                mid_y = (prev.y + y) / 2
                chord_ang = math.atan2(y - prev.y, x - prev.x)
                center_x = mid_x - radius * math.sin(angle / 2) * math.cos(chord_ang)
                center_y = mid_y - radius * math.sin(angle / 2) * math.sin(chord_ang)
                # Generate arc points
                start_ang = math.atan2(prev.y - center_y, prev.x - center_x)
                steps = max(4, int(abs(angle) / 0.3))
                for j in range(1, steps + 1):
                    a = start_ang + angle * j / steps
                    vertices.append(Point(center_x + radius * math.cos(a),
                                          center_y + radius * math.sin(a)))
                vertices.append(Point(x, y))
            else:
                vertices.append(Point(x, y))

        if len(vertices) >= 2:
            closed = entity.closed
            document.add_entity(Polyline(vertices, closed=closed,
                                         layer_name=_layer(entity),
                                         color=str(_aci(entity))))
            return True

    elif dxftype == "POLYLINE":
        pts = entity.points()
        vertices = [Point(p[0], p[1]) for p in pts]
        if len(vertices) >= 2:
            document.add_entity(Polyline(vertices,
                                         layer_name=_layer(entity),
                                         color=str(_aci(entity))))
            return True

    elif dxftype == "TEXT":
        insert = Point(entity.dxf.insert.x, entity.dxf.insert.y)
        content = entity.dxf.text
        height = entity.dxf.height if entity.dxf.hasattr('height') else 2.5
        document.add_entity(TextEntity(insert, content, height=height,
                                       layer_name=_layer(entity),
                                       color=str(_aci(entity))))
        return True

    elif dxftype == "MTEXT":
        insert = entity.dxf.insert if entity.dxf.hasattr('insert') else Point(0, 0)
        content = entity.text
        document.add_entity(TextEntity(
            Point(insert.x, insert.y) if hasattr(insert, 'x') else Point(0, 0),
            content,
            layer_name=_layer(entity),
            color=str(_aci(entity)),
        ))
        return True

    elif dxftype == "POINT":
        loc = entity.dxf.location
        document.add_entity(PointEntity(Point(loc.x, loc.y),
                                        layer_name=_layer(entity),
                                        color=str(_aci(entity))))
        return True

    elif dxftype == "DIMENSION":
        # Import linear dimensions
        try:
            p1 = Point(entity.dxf.def_point2.x, entity.dxf.def_point2.y)
            p2 = Point(entity.dxf.def_point3.x, entity.dxf.def_point3.y)
            tp = Point(entity.dxf.text_midpoint.x, entity.dxf.text_midpoint.y)
            document.add_entity(Dimension(p1, p2, tp,
                                          layer_name=_layer(entity),
                                          color=str(_aci(entity))))
            return True
        except Exception:
            pass

    return False


def _layer(entity) -> str:
    """Get layer name from DXF entity, default '0'."""
    try:
        return entity.dxf.layer
    except Exception:
        return "0"


def _aci(entity) -> int:
    """Get ACI color from DXF entity, default 7 (white)."""
    try:
        aci = entity.dxf.color
        if aci == 256:  # BYLAYER
            return 7
        return max(0, min(255, aci))
    except Exception:
        return 7
