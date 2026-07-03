"""
AutoCAD-style SCRIPT command: execute a .scr text file with drawing commands.

Format (one command per line, case-insensitive):
    LINE x1,y1 x2,y2
    CIRCLE cx,cy radius
    ARC cx,cy radius start_deg end_deg
    RECTANG x1,y1 x2,y2
    PLINE x1,y1 x2,y2 ...  [CLOSED]
    TEXT x,y content
    POINT x,y
    LAYER SET name
    LAYER NEW name
    ZOOM E
    ZOOM W x1,y1 x2,y2
    SAVE
    SAVEAS path
    DELAY ms
    ; comment line
"""

import re
from pathlib import Path
from src.model.entities.base import Point
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.point_entity import PointEntity
from src.model.entities.dimension import Dimension
from src.io.cad_file import save_document
import math


class ScriptEngine:
    """Parses and executes .scr script files."""

    def __init__(self, document, view, echo_fn, rebuild_fn):
        self.doc = document
        self.view = view
        self.echo = echo_fn
        self.rebuild = rebuild_fn
        self.layer = "0"
        self._line = 0

    def _parse_point(self, s: str) -> Point | None:
        """Parse 'x,y' or 'x, y' into Point."""
        s = s.strip()
        m = re.match(r'(-?[\d.]+)\s*,\s*(-?[\d.]+)', s)
        if m:
            return Point(float(m.group(1)), float(m.group(2)))
        return None

    def run(self, filepath: Path):
        """Execute a .scr file."""
        if not filepath.exists():
            self.echo(f"Script not found: {filepath}")
            return

        text = filepath.read_text()
        lines = text.strip().split('\n')
        self.echo(f"Running script: {filepath.name} ({len(lines)} lines)")

        for raw in lines:
            self._line += 1
            line = raw.strip()
            # Skip empty lines and comments
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            try:
                self._exec_line(line)
            except Exception as e:
                self.echo(f"  Line {self._line}: ERROR — {e}")
                break

        self.rebuild()
        self.echo("Script done. Command:")

    def _exec_line(self, line: str):
        """Execute a single command line."""
        parts = line.split(None, 1)  # split into COMMAND and ARGS
        if not parts:
            return
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "LINE":
            pts = args.split()
            if len(pts) >= 2:
                p1 = self._parse_point(pts[0])
                p2 = self._parse_point(pts[1])
                if p1 and p2:
                    self.doc.add_entity(Line(p1, p2, layer_name=self.layer))

        elif cmd == "CIRCLE":
            pts = args.split()
            if len(pts) >= 2:
                c = self._parse_point(pts[0])
                r = float(pts[1])
                if c:
                    self.doc.add_entity(Circle(c, r, layer_name=self.layer))

        elif cmd == "ARC":
            # ARC cx,cy radius start_deg end_deg
            pts = args.split()
            if len(pts) >= 4:
                c = self._parse_point(pts[0])
                r = float(pts[1])
                sa = math.radians(float(pts[2]))
                ea = math.radians(float(pts[3]))
                if c:
                    self.doc.add_entity(Arc(c, r, sa, ea, layer_name=self.layer))

        elif cmd == "RECTANG" or cmd == "RECTANGLE":
            pts = args.split()
            if len(pts) >= 2:
                p1 = self._parse_point(pts[0])
                p2 = self._parse_point(pts[1])
                if p1 and p2:
                    pl = Polyline([
                        Point(p1.x, p1.y), Point(p2.x, p1.y),
                        Point(p2.x, p2.y), Point(p1.x, p2.y),
                    ], closed=True, layer_name=self.layer)
                    self.doc.add_entity(pl)

        elif cmd == "PLINE" or cmd == "POLYLINE":
            pts_str = args.split()
            vertices = []
            closed = False
            for s in pts_str:
                if s.upper() == "CLOSED":
                    closed = True
                    continue
                pt = self._parse_point(s)
                if pt:
                    vertices.append(pt)
            if len(vertices) >= 2:
                self.doc.add_entity(Polyline(vertices, closed=closed,
                                             layer_name=self.layer))

        elif cmd == "TEXT" or cmd == "MTEXT":
            # TEXT x,y content (content can have spaces)
            m = re.match(r'(-?[\d.]+)\s*,\s*(-?[\d.]+)\s+(.*)', args)
            if m:
                pt = Point(float(m.group(1)), float(m.group(2)))
                content = m.group(3).strip().strip('"').strip("'")
                self.doc.add_entity(TextEntity(pt, content, layer_name=self.layer))

        elif cmd == "POINT":
            pt = self._parse_point(args)
            if pt:
                self.doc.add_entity(PointEntity(pt, layer_name=self.layer))

        elif cmd == "DIM" or cmd == "DIMENSION":
            pts = args.split()
            if len(pts) >= 3:
                p1 = self._parse_point(pts[0])
                p2 = self._parse_point(pts[1])
                tp = self._parse_point(pts[2])
                if p1 and p2 and tp:
                    self.doc.add_entity(Dimension(p1, p2, tp, layer_name=self.layer))

        elif cmd == "LAYER":
            parts = args.split(None, 1)
            if len(parts) >= 1:
                sub = parts[0].upper()
                val = parts[1] if len(parts) > 1 else ""
                lm = self.doc.layer_manager
                if sub == "SET" and val:
                    if val in lm.layers:
                        lm.set_current(val)
                        self.layer = val
                elif sub == "NEW" and val:
                    if val not in lm.layers:
                        lm.add_layer(val)
                    lm.set_current(val)
                    self.layer = val
                elif sub == "ON" and val:
                    if val in lm.layers:
                        lm.layers[val].visible = True
                elif sub == "OFF" and val:
                    if val in lm.layers:
                        lm.layers[val].visible = False
                elif sub == "COLOR" or sub == "COLOUR":
                    # LAYER COLOR layername #RRGGBB
                    parts2 = val.split()
                    if len(parts2) >= 2:
                        if parts2[0] in lm.layers:
                            lm.layers[parts2[0]].color = parts2[1]

        elif cmd == "ZOOM":
            sub = args.strip().upper()
            if sub == "E" or sub == "EXTENTS":
                # Will be done by rebuild
                pass
            elif sub.startswith("W"):
                pts = args.split()[1:] if len(args.split()) > 1 else []
                if len(pts) >= 2:
                    p1 = self._parse_point(pts[0])
                    p2 = self._parse_point(pts[1])
                    if p1 and p2:
                        from PySide6.QtCore import QRectF, QPointF
                        self.view.zoom_window(QRectF(
                            QPointF(p1.x, p1.y), QPointF(p2.x, p2.y)))

        elif cmd == "SAVE":
            if self.doc.filename:
                save_document(self.doc, Path(self.doc.filename))
            else:
                save_document(self.doc, Path("drawing.cadlite"))

        elif cmd == "SAVEAS":
            if args.strip():
                save_document(self.doc, Path(args.strip()))

        elif cmd == "ERASE" or cmd == "DELETE":
            if args.strip().upper() == "ALL":
                for uuid in list(self.doc._entities.keys()):
                    self.doc.remove_entity(uuid)
            else:
                # ERASE by layer
                for uuid in list(self.doc._entities.keys()):
                    ent = self.doc._entities.get(uuid)
                    if ent and ent.layer_name == args.strip():
                        self.doc.remove_entity(uuid)

        elif cmd == "DELAY":
            # DELAY milliseconds (for timing, useful in animations)
            try:
                ms = int(args.strip())
                import time
                time.sleep(ms / 1000.0)
            except ValueError:
                pass

        elif cmd == "UNDO":
            self.doc.undo()

        elif cmd == "REDO":
            self.doc.redo()

        # Unknown commands are silently ignored
