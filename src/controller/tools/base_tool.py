from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QCursor, QMouseEvent, QKeyEvent, QPen, QColor, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from src.model.entities.base import Point
from src.model.snap import SnapEngine, SnapType, SnapResult, osmode_to_snaps


class SnapIndicator(QGraphicsItem):
    """AutoCAD-style snap glyphs — different shapes per SnapType."""

    _SIZE = 5.0
    _PEN_W = 2.0

    _COLORS = {
        "default": QColor("#00FF00"),      # bright green
    }

    def __init__(self):
        super().__init__()
        self.setZValue(10000)
        self._snap_type: SnapType | None = None
        self.hide()

    def set_snap_type(self, st: SnapType | None):
        self._snap_type = st
        self.update()

    def boundingRect(self) -> QRectF:
        s = self._SIZE + self._PEN_W
        return QRectF(-s, -s, s * 2, s * 2)

    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(QColor("#00FF00"))
        pen.setWidthF(self._PEN_W)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        s = self._SIZE
        st = self._snap_type or SnapType.NEAREST

        if st == SnapType.ENDPOINT:
            # Square
            painter.drawRect(QRectF(-s, -s, s * 2, s * 2))

        elif st == SnapType.MIDPOINT:
            # Triangle △
            h = s * 1.732  # equilateral triangle height
            painter.drawPolygon([
                QPointF(0, -h * 0.67),
                QPointF(-s, h * 0.33),
                QPointF(s, h * 0.33),
            ])

        elif st == SnapType.CENTER:
            # Circle with crosshair
            painter.drawEllipse(QPointF(0, 0), s + 1, s + 1)
            painter.drawLine(QPointF(-s - 2, 0), QPointF(s + 2, 0))
            painter.drawLine(QPointF(0, -s - 2), QPointF(0, s + 2))

        elif st == SnapType.NODE:
            # Circle with dot
            painter.drawEllipse(QPointF(0, 0), s, s)
            painter.setBrush(QColor("#00FF00"))
            painter.drawEllipse(QPointF(0, 0), s * 0.3, s * 0.3)

        elif st == SnapType.QUADRANT:
            # Diamond ◇
            painter.drawPolygon([
                QPointF(0, -s - 1), QPointF(s + 1, 0),
                QPointF(0, s + 1), QPointF(-s - 1, 0),
            ])

        elif st == SnapType.INTERSECTION:
            # X
            painter.drawLine(QPointF(-s, -s), QPointF(s, s))
            painter.drawLine(QPointF(s, -s), QPointF(-s, s))

        elif st == SnapType.INSERTION:
            # Double square ⊞
            painter.drawRect(QRectF(-s, -s, s * 2, s * 2))
            painter.drawRect(QRectF(-s * 0.5, -s * 0.5, s, s))

        elif st == SnapType.PERPENDICULAR:
            # Right angle ┴
            painter.drawLine(QPointF(0, s + 2), QPointF(0, -s))
            painter.drawLine(QPointF(0, -s), QPointF(s, -s))
            painter.drawLine(QPointF(0, -s), QPointF(0, -s));
            # Small square at corner
            corner = s * 0.4
            painter.drawRect(QRectF(-corner, -s - corner, corner, corner))

        elif st == SnapType.TANGENT:
            # Circle with tangent line
            painter.drawEllipse(QPointF(0, 0), s, s)
            painter.drawLine(QPointF(s, 0), QPointF(s + s, 0))

        elif st == SnapType.NEAREST:
            # Hourglass ⧖
            painter.drawLine(QPointF(-s, -s), QPointF(s, s))
            painter.drawLine(QPointF(s, -s), QPointF(-s, s))
            painter.drawLine(QPointF(-s * 0.4, -s * 0.4), QPointF(s * 0.4, s * 0.4))
            painter.drawLine(QPointF(s * 0.4, -s * 0.4), QPointF(-s * 0.4, s * 0.4))

        else:
            # Default: small cross
            painter.drawLine(QPointF(-s, 0), QPointF(s, 0))
            painter.drawLine(QPointF(0, -s), QPointF(0, s))


class BaseTool:
    def __init__(self, view, document):
        self.view = view
        self.document = document
        self._snap_engine = SnapEngine(snap_distance=15.0)
        self._snap_indicator = SnapIndicator()
        self._last_snap: SnapResult | None = None
        self._snap_pixels = 50  # generous aperture (~8% viewport)
        self._transient_snap: SnapType | None = None  # single-pick override

    def set_transient_snap(self, name: str) -> bool:
        """Set a single-pick OSNAP override. Returns True if valid snap name."""
        from src.model.snap import OSMODE_NAMES, _OSMODE_REVERSE
        name_upper = name.strip().upper()
        if name_upper in OSMODE_NAMES:
            bit = OSMODE_NAMES[name_upper]
            self._transient_snap = _OSMODE_REVERSE[bit]
            return True
        return False

    def _clear_transient_snap(self):
        """Consume the transient snap after a pick."""
        self._transient_snap = None

    @property
    def _active_snaps(self) -> set[SnapType]:
        """Read active snap modes from OSMODE sysvar."""
        try:
            osmode = int(self.document.sysvars["OSMODE"])
        except Exception:
            osmode = 0
        snaps = osmode_to_snaps(osmode)
        # OSMODE=0 means no running snaps (AutoCAD behavior)
        return snaps

    @property
    def _current_layer(self) -> str:
        """Read CLAYER from sysvars."""
        try:
            return self.document.sysvars["CLAYER"]
        except Exception:
            return "0"

    @property
    def _current_linetype(self) -> str:
        """Read CELTYPE from sysvars, resolving BYLAYER to layer linetype."""
        try:
            celt = self.document.sysvars["CELTYPE"]
        except Exception:
            return "CONTINUOUS"
        if isinstance(celt, str) and celt.upper() == "BYLAYER":
            try:
                lm = self.document.layer_manager
                return lm.layers[lm.current_layer_name].linetype
            except Exception:
                return "CONTINUOUS"
        return celt
        if isinstance(cec, str) and cec.upper() == "BYLAYER":
            # Resolve to current layer's color
            try:
                lm = self.document.layer_manager
                return lm.layers[lm.current_layer_name].color
            except Exception:
                return "7"
        return cec

    @property
    def _current_layer(self) -> str:
        """Current layer name from layer_manager."""
        return self.document.layer_manager.current_layer_name

    @property
    def _current_color(self) -> str:
        """Read CECOLOR from sysvars, resolving BYLAYER to layer color."""
        try:
            cec = self.document.sysvars["CECOLOR"]
        except Exception:
            return "7"
        if isinstance(cec, str) and cec.upper() == "BYLAYER":
            try:
                lm = self.document.layer_manager
                return lm.layers[lm.current_layer_name].color
            except Exception:
                return "7"
        return cec

    @property
    def _current_linetype(self) -> str:
        """Read CELTYPE from sysvars, resolving BYLAYER to layer linetype."""
        try:
            celt = self.document.sysvars["CELTYPE"]
        except Exception:
            return "CONTINUOUS"
        if isinstance(celt, str) and celt.upper() == "BYLAYER":
            try:
                lm = self.document.layer_manager
                return lm.layers[lm.current_layer_name].linetype
            except Exception:
                return "CONTINUOUS"
        return celt

    def activate(self):
        if self._snap_indicator.scene() is None:
            self.view.scene().addItem(self._snap_indicator)

    def deactivate(self):
        self._clear_snap_indicator()
        self._transient_snap = None
        if self._snap_indicator.scene():
            self.view.scene().removeItem(self._snap_indicator)

    def cursor(self) -> QCursor:
        return QCursor(Qt.CursorShape.ArrowCursor)

    def _pixel_to_scene_distance(self) -> float:
        """Convert snap_pixels to scene units based on current zoom level."""
        viewport = self.view.viewport()
        if viewport is None or viewport.width() == 0:
            return 15.0
        # Map a pixel distance to scene coordinates
        p1 = self.view.mapToScene(0, 0)
        p2 = self.view.mapToScene(self._snap_pixels, 0)
        dx = p2.x() - p1.x()
        return abs(dx)

    def _snap(self, scene_pos: QPointF, ref_point: Point | None = None) -> Point:
        """Snap the given scene position to nearby geometry. ref_point = first point for PER/TAN."""
        cursor = Point(scene_pos.x(), scene_pos.y())
        self._snap_engine.snap_distance = self._pixel_to_scene_distance()

        # Read SNAPUNIT from sysvars for grid snap
        try:
            raw = self.document.sysvars["SNAPUNIT"]
            if isinstance(raw, str):
                parts = raw.split(',')
                self._snap_engine._snap_unit = (float(parts[0]), float(parts[1]))
        except Exception:
            self._snap_engine._snap_unit = (1.0, 1.0)

        # Transient OSNAP override: single-pick snap (e.g. LINE END → pick → PER → pick)
        active = set(self._active_snaps)
        if self._transient_snap is not None:
            # Override: use ONLY the transient snap for this pick
            # Don't clear here — mouse_move also calls _snap and would consume it.
            # Instead, mouse_press clears it after the actual pick.
            active = {self._transient_snap}
        try:
            if int(self.document.sysvars["SNAPMODE"]):
                active.add(SnapType.GRID)
        except Exception:
            pass

        result = self._snap_engine.find_snap(
            cursor, self.document.entities, active, ref_point
        )
        if result:
            self._last_snap = result
            self._snap_indicator.setPos(QPointF(result.point.x, result.point.y))
            self._snap_indicator.set_snap_type(result.snap_type)
            self._snap_indicator.show()
            return result.point
        else:
            self._last_snap = None
            self._snap_indicator.hide()
            return cursor

    def _clear_snap_indicator(self):
        self._snap_indicator.hide()
        self._last_snap = None

    def mouse_press(self, event: QMouseEvent, scene_pos: QPointF): ...
    def mouse_move(self, event: QMouseEvent, scene_pos: QPointF): ...
    def mouse_release(self, event: QMouseEvent, scene_pos: QPointF): ...
    def key_press(self, event: QKeyEvent): ...
