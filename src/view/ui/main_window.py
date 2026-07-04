from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QToolBar, QStatusBar, QDockWidget,
    QListWidget, QListWidgetItem, QPlainTextEdit,
    QFileDialog, QMessageBox, QInputDialog,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem,
)
from PySide6.QtGui import QAction, QKeySequence, QColor, QFont, QPalette
from PySide6.QtCore import Qt, QPointF, QTimer
from pathlib import Path

from src.view.cad_scene import CadScene
from src.view.cad_view import CadView
from src.view.graphics.grid_item import GridItem
from src.model.document import Document
from src.controller.tool_manager import ToolManager
from src.controller.tools.line_tool import LineTool
from src.controller.tools.circle_tool import CircleTool
from src.controller.tools.arc_tool import ArcTool
from src.controller.tools.polyline_tool import PolylineTool
from src.controller.tools.rectangle_tool import RectangleTool
from src.controller.tools.text_tool import TextTool
from src.controller.tools.dim_linear_tool import DimLinearTool
from src.controller.tools.dim_radius_tool import DimRadiusTool
from src.controller.tools.select_tool import SelectTool
from src.controller.tools.stretch_tool import StretchTool
from src.controller.tools.ellipse_tool import EllipseTool
from src.controller.tools.move_tool import MoveTool
from src.controller.tools.copy_tool import CopyTool
from src.controller.tools.rotate_tool import RotateTool
from src.controller.tools.delete_tool import DeleteTool
from src.controller.tools.zoom_win_tool import ZoomWinTool
from src.controller.tools.pan_tool import PanTool
from src.controller.tools.dist_tool import DistTool
from src.controller.tools.id_tool import IdTool
from src.controller.tools.area_tool import AreaTool
from src.controller.tools.mirror_tool import MirrorTool
from src.controller.tools.scale_tool import ScaleTool
from src.controller.tools.offset_tool import OffsetTool
from src.controller.tools.trim_tool import TrimTool
from src.controller.tools.extend_tool import ExtendTool
from src.controller.tools.fillet_tool import FilletTool
from src.controller.tools.chamfer_tool import ChamferTool
from src.controller.tools.explode_tool import ExplodeTool
from src.controller.tools.break_tool import BreakTool
from src.controller.tools.array_tool import ArrayTool
from src.controller.tools.hatch_tool import HatchTool
from src.controller.tools.point_tool import PointTool
from src.controller.tools.solid_tool import SolidTool
from src.io.cad_file import save_document, load_document
from src.io.dxf_export import export_dxf


# ── AutoCAD 10 style color palette ──
CLR_BG         = "#000000"   # black drawing area
CLR_GRID       = "#0a1a2a"   # dark blue grid
CLR_TEXT       = "#FFFFFF"   # white text everywhere
CLR_MENU_BG    = "#000022"   # dark navy menu bg
CLR_MENU_TEXT  = "#FFFFFF"   # white menu text
CLR_MENU_SEL   = "#003388"   # blue selection
CLR_STATUS_BG  = "#000022"
CLR_CMD_BG     = "#000018"
CLR_CMD_TEXT   = "#FFFFFF"
CLR_ACCENT     = "#FFCC00"   # yellow accent (snap, warnings)
CLR_HEADER     = "#44AAFF"   # blue header text in screen menu
CLR_SCREEN_BG  = "#0000AA"   # classic ACAD blue (VGA palette)
CLR_INFO_BG    = "#000088"   # info bar darker blue


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DogCAD 2D Lite")
        self.resize(1280, 800)

        self._document = Document()
        self._filename: Path | None = None

        self._init_scene()
        self._init_tools()
        self._setup_menus()
        self._setup_screen_menu()
        self._setup_command_line()
        self._apply_theme()

        # Focus the view so keyboard shortcuts work immediately
        self._view.setFocus()

    # ── Theme ──────────────────────────────────────────────
    def _apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CLR_MENU_BG};
            }}
            QMenuBar {{
                background-color: {CLR_MENU_BG};
                color: {CLR_MENU_TEXT};
                border-bottom: 1px solid #1a1a2e;
            }}
            QMenuBar::item:selected {{
                background-color: {CLR_MENU_SEL};
            }}
            QMenu {{
                background-color: {CLR_MENU_BG};
                color: {CLR_MENU_TEXT};
                border: 1px solid #1a1a2e;
            }}
            QMenu::item:selected {{
                background-color: {CLR_MENU_SEL};
            }}
            QListWidget {{
                background-color: {CLR_SCREEN_BG};
                color: {CLR_MENU_TEXT};
                border: none;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 4px 6px;
            }}
            QListWidget::item:selected {{
                background-color: {CLR_MENU_SEL};
            }}
            QListWidget::item:hover {{
                background-color: #002266;
            }}
            QPlainTextEdit {{
                background-color: {CLR_CMD_BG};
                color: {CLR_CMD_TEXT};
                border: 1px solid #1a1a2e;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
            QStatusBar {{
                background-color: {CLR_STATUS_BG};
                color: {CLR_TEXT};
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border-top: 1px solid #1a1a2e;
            }}
            QDockWidget {{
                color: {CLR_MENU_TEXT};
                titlebar-close-icon: none;
            }}
            QDockWidget::title {{
                background-color: {CLR_MENU_BG};
                border-bottom: 1px solid #1a1a2e;
                padding: 4px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                text-align: center;
            }}
        """)

    # ── Scene + View ───────────────────────────────────────
    def _init_scene(self):
        self._scene = CadScene()
        self._view = CadView(self._scene)
        self.setCentralWidget(self._view)

        self._grid = GridItem(self._scene.sceneRect(), spacing=10.0)
        self._scene.addItem(self._grid)

        self._view._status_callback = self._update_coord_status

        # Start with select tool cursor feedback
        self._snap_active = True
        self._ortho_active = False

    # ── Tools ──────────────────────────────────────────────
    def _init_tools(self):
        lm = self._document.layer_manager
        d = self._document
        v = self._view
        self._tool_manager = ToolManager(v, d)

        self._tool_manager.register_tool("select", SelectTool(v, d))
        self._tool_manager.register_tool("stretch", StretchTool(v, d, lm))
        self._tool_manager.register_tool("ellipse", EllipseTool(v, d, lm))
        self._tool_manager.register_tool("line", LineTool(v, d, lm))
        self._tool_manager.register_tool("circle", CircleTool(v, d, lm))
        self._tool_manager.register_tool("arc", ArcTool(v, d, lm))
        self._tool_manager.register_tool("polyline", PolylineTool(v, d, lm))
        self._tool_manager.register_tool("rectangle", RectangleTool(v, d, lm))
        self._tool_manager.register_tool("text", TextTool(v, d, lm))
        self._tool_manager.register_tool("dim", DimLinearTool(v, d, lm))
        self._tool_manager.register_tool("move", MoveTool(v, d))
        self._tool_manager.register_tool("copy", CopyTool(v, d))
        self._tool_manager.register_tool("rotate", RotateTool(v, d))
        self._tool_manager.register_tool("delete", DeleteTool(v, d))
        self._tool_manager.register_tool("zoomwin", ZoomWinTool(v, d))
        self._tool_manager.register_tool("pan", PanTool(v, d))
        self._tool_manager.register_tool("dist", DistTool(v, d, self._echo))
        self._tool_manager.register_tool("id", IdTool(v, d, self._echo))
        self._tool_manager.register_tool("area", AreaTool(v, d, self._echo))
        self._tool_manager.register_tool("mirror", MirrorTool(v, d))
        self._tool_manager.register_tool("scale", ScaleTool(v, d))
        self._tool_manager.register_tool("offset", OffsetTool(v, d))
        self._tool_manager.register_tool("trim", TrimTool(v, d))
        self._tool_manager.register_tool("extend", ExtendTool(v, d))
        self._tool_manager.register_tool("fillet", FilletTool(v, d))
        self._tool_manager.register_tool("chamfer", ChamferTool(v, d))
        self._tool_manager.register_tool("explode", ExplodeTool(v, d))
        self._tool_manager.register_tool("break", BreakTool(v, d))
        self._tool_manager.register_tool("array", ArrayTool(v, d))
        self._tool_manager.register_tool("hatch", HatchTool(v, d))
        self._tool_manager.register_tool("point", PointTool(v, d, lm))
        self._tool_manager.register_tool("solid", SolidTool(v, d, lm))
        self._tool_manager.register_tool("dimradius", DimRadiusTool(v, d, lm))

        self._view.tool_manager = self._tool_manager

        # ── Status Bar (ACAD 10 style with picante ASCII) ──
        self._sb_layer = QLabel("LAYER:0")
        self._sb_color = QLabel("COLOR:White")
        self._sb_ltype = QLabel("LINETYPE:Continuous")
        self._sb_coords = QLabel("X=     0.0000  Y=     0.0000")
        self._sb_file = QLabel("NEW")
        self._sb_ortho = QLabel("")
        self._sb_snap = QLabel("")

        sb = QStatusBar()
        sb.setStyleSheet(f"""
            QStatusBar {{
                background-color: {CLR_INFO_BG};
                border-top: 2px solid #000055;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: {CLR_MENU_TEXT};
            }}
            QLabel {{
                color: {CLR_MENU_TEXT};
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 0 6px;
            }}
        """)
        sb.addWidget(self._sb_layer)
        sb.addWidget(self._sb_color)
        sb.addWidget(self._sb_ltype)
        sb.addWidget(self._sb_coords)
        sb.addPermanentWidget(self._sb_file)
        sb.addPermanentWidget(self._sb_snap)
        sb.addPermanentWidget(self._sb_ortho)
        self.setStatusBar(sb)

        self._tool_manager.activate_tool("select")

    def _activate_tool(self, name: str):
        """Activate tool and echo command to command line."""
        if name in self._tool_manager._tools:
            # If switching away from a modify tool, rebuild scene
            old_tool = self._tool_manager._active_tool
            if old_tool and type(old_tool).__name__ in (
                "MoveTool", "CopyTool", "RotateTool", "MirrorTool",
                "ScaleTool", "TrimTool", "ExtendTool", "FilletTool",
                "ChamferTool", "BreakTool", "ExplodeTool",
            ):
                self._rebuild_scene()
            self._tool_manager.activate_tool(name)
            self._echo_command(name)
            self._update_screen_menu_highlight(name)

    # ── Menus (pull-down) ──────────────────────────────────
    def _setup_menus(self):
        mb = self.menuBar()

        # File
        m = mb.addMenu("FILE")
        m.addAction("NEW", self._on_new, QKeySequence.StandardKey.New)
        m.addAction("OPEN", self._on_open, QKeySequence.StandardKey.Open)
        m.addAction("SAVE", self._on_save, QKeySequence.StandardKey.Save)
        m.addAction("SAVE AS", self._on_save_as, "Ctrl+Shift+S")
        m.addSeparator()
        m.addAction("DXF OUT", self._on_export_dxf)
        m.addSeparator()
        m.addAction("SCRIPT", self._on_script)
        m.addSeparator()
        m.addAction("ACERCA DE", self._on_about)
        m.addSeparator()
        m.addAction("QUIT", self.close, QKeySequence.StandardKey.Quit)

        # Edit
        m = mb.addMenu("EDIT")
        m.addAction("UNDO", self._on_undo, QKeySequence.StandardKey.Undo)
        m.addAction("REDO", self._on_redo, QKeySequence.StandardKey.Redo)
        m.addSeparator()
        m.addAction("ERASE", self._on_erase)
        m.addAction("ERASE ALL", self._on_erase_all)

        # Draw
        m = mb.addMenu("DRAW")
        m.addAction("LINE", lambda: self._activate_tool("line"))
        m.addAction("CIRCLE", lambda: self._activate_tool("circle"))
        m.addAction("ARC", lambda: self._activate_tool("arc"))
        m.addAction("PLINE", lambda: self._activate_tool("polyline"))
        m.addAction("RECTANG", lambda: self._activate_tool("rectangle"))
        m.addAction("TEXT", lambda: self._activate_tool("text"))
        m.addAction("DIM", lambda: self._activate_tool("dim"))

        # Modify
        m = mb.addMenu("MODIFY")
        m.addAction("MOVE", lambda: self._activate_tool("move"), "M")
        m.addAction("COPY", lambda: self._activate_tool("copy"))
        m.addAction("ROTATE", lambda: self._activate_tool("rotate"))

        # Display
        m = mb.addMenu("DISPLAY")
        m.addAction("ZOOM EXTENTS", self._view.zoom_extents)
        m.addAction("REDRAW", self._rebuild_scene)

        # Inquiry
        m = mb.addMenu("INQUIRY")
        m.addAction("LIST ENTITIES", self._on_list_entities)

        # Layer
        m = mb.addMenu("LAYER")
        m.addAction("LAYERS...", self._show_layer_dialog)

        # Settings
        m = mb.addMenu("SETTINGS")
        snap_act = QAction("SNAP  (F9)", self, checkable=True)
        snap_act.setChecked(True)
        snap_act.triggered.connect(self._toggle_snap)
        m.addAction(snap_act)
        self._snap_action = snap_act

        ortho_act = QAction("ORTHO (F8)", self, checkable=True)
        ortho_act.setChecked(False)
        ortho_act.triggered.connect(self._toggle_ortho)
        m.addAction(ortho_act)
        self._ortho_action = ortho_act

    # ── Screen Menu (right side) ───────────────────────────
    def _setup_screen_menu(self):
        dock = QDockWidget("SCREEN MENU", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self._screen_menu = QListWidget()
        self._screen_menu.setFixedWidth(160)
        self._screen_menu.itemClicked.connect(self._on_screen_menu_click)

        dock.setWidget(self._screen_menu)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        # Initial state: root menu
        self._screen_menu_state = "root"
        self._refresh_screen_menu()

        # Keyboard shortcuts for screen menu navigation
        self._key_aliases = {
            Qt.Key.Key_L: "line", Qt.Key.Key_C: "circle", Qt.Key.Key_A: "arc",
            Qt.Key.Key_P: "polyline", Qt.Key.Key_R: "rectangle",
            Qt.Key.Key_T: "text", Qt.Key.Key_D: "dim",
            Qt.Key.Key_M: "move", Qt.Key.Key_Escape: "select",
            Qt.Key.Key_Delete: "erase",
        }

    def _refresh_screen_menu(self):
        self._screen_menu.clear()
        S = self._screen_menu_state

        if S == "root":
            items = [
                ("DogCAD 2D", None),
                ("* * * *", None), ("", None),
                ("DRAW    ", "menu_draw"),
                ("EDIT    ", "menu_edit"),
                ("DISPLAY ", "menu_display"),
                ("INQUIRY ", "menu_inquiry"),
                ("LAYER   ", "menu_layer"),
                ("DIM     ", "menu_dimension"),
                ("SETTINGS", "menu_settings"),
                ("UTILITY ", "menu_utility"),
                ("", None),
                ("  SAVE  ", "save"),
                ("  OPEN  ", "open"),
                ("  DXF OUT","dxf"),
                ("", None),
                ("  QUIT  ", "quit"),
            ]
        elif S == "menu_draw":
            items = [
                ("  DRAW  ", None), ("", None),
                (" LINE   ", "line"),
                (" ARC    ", "arc"),
                (" CIRCLE ", "circle"),
                (" PLINE  ", "polyline"),
                (" RECTANG", "rectangle"),
                (" TEXT   ", "text"),
                (" DIM    ", "dim"),
                (" POINT  ", "point"),
                (" ELLIPSE", "ellipse"),
                (" HATCH  ", "hatch"),
                (" SOLID  ", "solid"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_edit":
            items = [
                ("  EDIT  ", None), ("", None),
                (" ERASE  ", "erase"),
                (" MOVE   ", "move"),
                (" COPY   ", "copy"),
                (" ROTATE ", "rotate"),
                (" MIRROR ", "mirror"),
                (" SCALE  ", "scale"),
                (" OFFSET ", "offset"),
                (" TRIM   ", "trim"),
                (" EXTEND ", "extend"),
                (" FILLET ", "fillet"),
                (" CHAMFER", "chamfer"),
                (" BREAK  ", "break"),
                (" EXPLODE", "explode"),
                (" ARRAY  ", "array"),
                (" STRETCH", "stretch"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_display":
            items = [
                (" DISPLAY", None), ("", None),
                (" ZOOM E ", "zoom_extents"),
                (" ZOOM W ", "zoom_window"),
                (" ZOOM P ", "zoom_previous"),
                (" PAN    ", "pan_cmd"),
                (" REDRAW ", "redraw"),
                (" REGEN  ", "regen"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_inquiry":
            items = [
                (" INQUIRY", None), ("", None),
                (" LIST   ", "list_entities"),
                (" DIST   ", "dist"),
                (" AREA   ", "area"),
                (" ID     ", "id_cmd"),
                (" STATUS ", "status_cmd"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_layer":
            items = [
                ("  LAYER  ", None), ("", None),
                (" ?      ", "layer_query"),
                (" MAKE   ", "layer_make"),
                (" SET    ", "layer_set"),
                (" NEW    ", "layer_new"),
                (" ON     ", "layer_on"),
                (" OFF    ", "layer_off"),
                (" COLOR  ", "layer_color"),
                (" LINETYPE","ni_ltype"),
                (" FREEZE ", "layer_freeze"),
                (" THAW   ", "layer_thaw"),
                (" LOCK   ", "layer_lock"),
                (" UNLOCK ", "layer_unlock"),
                (" DELETE ", "layer_del"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_dimension":
            items = [
                (" DIM    ", None), ("", None),
                (" LINEAR ", "dim"),
                (" ALIGNED", "dim_aligned"),
                (" RADIUS ", "dim_radius"),
                (" DIAMETR", "dim_diameter"),
                (" ANGULAR", "dim_angular"),
                ("", None),
                (" SETVAR ", "ni_setvardim"),
                ("  DIMSCALE", "ni_dimscale"),
                ("  DIMTXT  ", "ni_dimtxt"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_settings":
            items = [
                (" SETTINGS", None), ("", None),
                (" SNAP   ", "snap_toggle"),
                (" GRID   ", "grid_toggle"),
                (" ORTHO  ", "ortho_toggle"),
                (" COLOR  ", "ni_color"),
                (" LINETYPE","ni_ltype"),
                (" UNITS  ", "units"),
                (" LIMITS ", "limits"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        elif S == "menu_utility":
            items = [
                (" UTILITY ", None), ("", None),
                (" UNDO   ", "undo"),
                (" REDO   ", "redo"),
                (" PURGE  ", "purge"),
                (" PLOT   ", "plot"),
                (" DXFIN  ", "ni_dxfin"),
                (" SCRIPT ", "script_cmd"),
                (" TEMPLATE","ni_template"),
                ("", None),
                (" [<-BACK]", "root"),
            ]
        else:
            items = []

        for label, action in items:
            if label == "":
                item = QListWidgetItem("")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self._screen_menu.addItem(item)
                continue
            display = label.strip()
            item = QListWidgetItem(display)
            is_nav = label.startswith("[<-")
            is_header = action is None and not is_nav

            if is_header:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setForeground(QColor(CLR_HEADER))
            elif is_nav:
                item.setData(Qt.ItemDataRole.UserRole, action)
                item.setForeground(QColor("#FFCC00"))
            else:
                item.setData(Qt.ItemDataRole.UserRole, action)
                item.setForeground(QColor(CLR_MENU_TEXT))

            self._screen_menu.addItem(item)

    def _on_screen_menu_click(self, item: QListWidgetItem):
        action = item.data(Qt.ItemDataRole.UserRole)
        if not action:
            return

        if action in ("menu_draw", "menu_edit", "menu_display",
                       "menu_layer", "menu_dimension", "menu_settings",
                       "menu_inquiry", "menu_utility", "root"):
            self._screen_menu_state = action
            self._refresh_screen_menu()
        elif action == "save":
            self._on_save()
        elif action == "open":
            self._on_open()
        elif action == "dxf":
            self._on_export_dxf()
        elif action == "quit":
            self.close()
        elif action == "erase":
            self._on_erase()
        elif action == "undo":
            self._on_undo()
        elif action == "redo":
            self._on_redo()
        elif action == "zoom_extents":
            self._view.zoom_extents()
            self._echo("ZOOM Extents")
            self._echo("Command:")
        elif action == "zoom_previous":
            self._view.zoom_previous()
            self._echo("ZOOM Previous")
            self._echo("Command:")
        elif action == "redraw":
            self._rebuild_scene()
            self._echo("REDRAW")
            self._echo("Command:")
        elif action == "snap_toggle":
            self._toggle_snap()
        elif action == "ortho_toggle":
            self._toggle_ortho()
        elif action == "grid_toggle":
            self._grid.setVisible(not self._grid.isVisible())
        elif action == "layer_set":
            # Set current layer from menu
            layers = list(self._document.layer_manager.layers.keys())
            name, ok = QInputDialog.getItem(self, "Set Layer", "Layer:", layers, 0, False)
            if ok and name:
                self._document.layer_manager.set_current(name)
        elif action == "layer_new":
            name, ok = QInputDialog.getText(self, "New Layer", "Layer name:")
            if ok and name.strip():
                try:
                    self._document.layer_manager.add_layer(name.strip())
                except ValueError as e:
                    QMessageBox.warning(self, "Error", str(e))
        elif action == "layer_del":
            layers = [n for n in self._document.layer_manager.layers if n != "0"]
            if layers:
                name, ok = QInputDialog.getItem(self, "Delete Layer", "Layer:", layers, 0, False)
                if ok and name:
                    self._document.layer_manager.delete_layer(name)
        elif action == "list_entities":
            self._on_list_entities()
        # ── Layer operations ──
        elif action == "layer_on":
            self._layer_op("ON", lambda l: setattr(l, 'visible', True))
        elif action == "layer_off":
            self._layer_op("OFF", lambda l: setattr(l, 'visible', False))
        elif action == "layer_freeze":
            self._layer_op("FREEZE", lambda l: setattr(l, 'locked', True))
        elif action == "layer_thaw":
            self._layer_op("THAW", lambda l: setattr(l, 'locked', False))
        elif action == "layer_lock":
            self._layer_op("LOCK", lambda l: setattr(l, 'locked', True))
        elif action == "layer_unlock":
            self._layer_op("UNLOCK", lambda l: setattr(l, 'locked', False))
        elif action == "layer_color":
            self._layer_color()
        elif action == "layer_make":
            self._layer_make()
        elif action == "layer_query":
            self._layer_query()
        # ── Display ──
        elif action == "zoom_window":
            self._activate_tool("zoomwin")
            self._echo("ZOOM Window — drag rectangle to zoom")
            self._echo("Command:")
        elif action == "pan_cmd":
            self._activate_tool("pan")
            self._echo("PAN — drag to pan")
            self._echo("Command:")
        elif action == "regen":
            self._rebuild_scene()
            self._echo("Regenerating drawing.")
            self._echo("Command:")
        # ── Inquiry ──
        elif action == "dist":
            self._activate_tool("dist")
        elif action == "id_cmd":
            self._on_id()
        elif action == "status_cmd":
            self._on_status()
        elif action == "area":
            self._activate_tool("area")
        elif action == "purge":
            self._on_purge()
        elif action == "units":
            self._on_units()
        elif action == "limits":
            self._on_limits()
        elif action == "plot":
            self._on_plot()
        elif action == "script_cmd":
            self._on_script()
        elif action == "insert_cmd":
            self._activate_tool("insert")
        # ── Not implemented echo ──
        elif action == "dim_aligned":
            self._tool_manager._aligned_dim = True
            self._activate_tool("dim")
        elif action == "dim_radius":
            self._tool_manager._dim_type = "radius"
            self._activate_tool("dimradius")
        elif action == "dim_diameter":
            self._tool_manager._dim_type = "diameter"
            self._activate_tool("dimradius")
        elif action == "dim_angular":
            self._tool_manager._dim_type = "angular"
            self._activate_tool("dimradius")
        elif action and action.startswith("ni_"):
            cmd_name = action[3:].upper()
            self._echo(f"Command: {cmd_name} (not implemented)")
            self._echo("Command:")
        elif action in self._tool_manager._tools:
            self._activate_tool(action)

    def _update_screen_menu_highlight(self, tool_name: str):
        """Highlight the active tool in the screen menu."""
        for i in range(self._screen_menu.count()):
            item = self._screen_menu.item(i)
            a = item.data(Qt.ItemDataRole.UserRole)
            if a == tool_name:
                item.setForeground(QColor("#FFCC00"))
            elif a and a not in ("menu_draw", "menu_edit", "menu_display",
                                  "menu_layer", "menu_settings", "root",
                                  "save", "open", "dxf", "quit", "erase",
                                  "undo", "redo", "zoom_extents", "redraw",
                                  "snap_toggle", "ortho_toggle", "grid_toggle",
                                  "layer_set", "layer_new", "layer_del"):
                item.setForeground(QColor(CLR_MENU_TEXT))

    # ── Command Line (bottom, multi-line) ──────────────────
    def _setup_command_line(self):
        dock = QDockWidget("COMMAND:", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self._cmd_output = QPlainTextEdit()
        self._cmd_output.setReadOnly(True)
        self._cmd_output.setMaximumBlockCount(500)
        self._cmd_output.setFixedHeight(80)
        self._cmd_output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._cmd_input = QPlainTextEdit()
        self._cmd_input.setFixedHeight(24)
        self._cmd_input.setPlaceholderText("Command:")
        self._cmd_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cmd_input.setTabChangesFocus(False)
        self._cmd_input.setCursorWidth(3)  # thick blinking cursor
        self._cmd_input.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                border: none;
                padding: 2px 6px;
            }
        """)

        # Capture Enter
        self._cmd_input.installEventFilter(self)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._cmd_output)
        layout.addWidget(self._cmd_input)

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        # Command history
        self._cmd_history: list[str] = []
        self._cmd_history_index: int = -1
        self._cmd_history_draft: str = ""  # saved text before navigating history

        self._echo("DogCAD 2D Lite — Type a command or use screen menu")
        self._echo("Command:")

    def eventFilter(self, obj, event):
        """Capture Enter, Up/Down arrows in command input."""
        from PySide6.QtCore import QEvent
        if obj == self._cmd_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()

            if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                text = self._cmd_input.toPlainText().strip()
                self._cmd_input.clear()
                if text:
                    self._cmd_history.append(text)
                    self._cmd_history_index = len(self._cmd_history)
                    self._process_command(text)
                return True

            if key == Qt.Key.Key_Up:
                # Save current draft if first time navigating
                if self._cmd_history_index == len(self._cmd_history):
                    self._cmd_history_draft = self._cmd_input.toPlainText()
                if self._cmd_history_index > 0:
                    self._cmd_history_index -= 1
                    self._cmd_input.setPlainText(self._cmd_history[self._cmd_history_index])
                    self._move_cursor_to_end()
                return True

            if key == Qt.Key.Key_Down:
                if self._cmd_history_index < len(self._cmd_history) - 1:
                    self._cmd_history_index += 1
                    self._cmd_input.setPlainText(self._cmd_history[self._cmd_history_index])
                    self._move_cursor_to_end()
                elif self._cmd_history_index == len(self._cmd_history) - 1:
                    # Back to the draft the user was typing
                    self._cmd_history_index = len(self._cmd_history)
                    self._cmd_input.setPlainText(self._cmd_history_draft)
                    self._move_cursor_to_end()
                return True

        return super().eventFilter(obj, event)

    def _move_cursor_to_end(self):
        """Move text cursor to the end of the command input."""
        cursor = self._cmd_input.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._cmd_input.setTextCursor(cursor)

    def _echo(self, text: str):
        self._cmd_output.appendPlainText(text)
        # Scroll to bottom
        self._cmd_output.verticalScrollBar().setValue(
            self._cmd_output.verticalScrollBar().maximum())

    def _echo_command(self, tool_name: str):
        """Show the command that was activated."""
        name_map = {
            "line": "LINE", "circle": "CIRCLE", "arc": "ARC",
            "polyline": "PLINE", "rectangle": "RECTANG",
            "text": "TEXT", "dim": "DIM",
            "move": "MOVE", "copy": "COPY", "rotate": "ROTATE",
            "delete": "ERASE", "select": "SELECT",
        }
        self._echo(f"Command: {name_map.get(tool_name, tool_name.upper())}")

    def _process_command(self, text: str):
        parts = text.strip().split(None, 1)
        if not parts:
            return
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        # Commands that take coordinates — delegate to ScriptEngine
        coord_commands = {
            "LINE", "L", "CIRCLE", "C", "ARC", "A",
            "RECTANG", "RECTANGLE", "REC", "R",
            "PLINE", "POLYLINE", "PL", "P",
            "TEXT", "T", "MTEXT", "POINT",
            "DIM", "DIMENSION", "D", "DIMALIGNED", "DIMLIN",
            "ERASE", "E", "LAYER", "ZOOM",
            "UNDO", "U", "REDO", "SAVE", "SAVEAS", "DELAY",
        }

        if cmd in coord_commands and args:
            # Execute directly via ScriptEngine
            from src.io.script_engine import ScriptEngine
            engine = ScriptEngine(
                self._document, self._view,
                self._echo, self._rebuild_scene)
            engine._exec_line(text)
            self._rebuild_scene()
            self._echo("Command:")
            return

        # Tool switching (bare commands without coordinates)
        aliases = {
            "L": "line", "LINE": "line",
            "C": "circle", "CIRCLE": "circle",
            "A": "arc", "ARC": "arc",
            "P": "polyline", "PL": "polyline", "PLINE": "polyline",
            "R": "rectangle", "REC": "rectangle", "RECTANG": "rectangle",
            "T": "text", "TEXT": "text",
            "D": "dim", "DIM": "dim",
            "DIMALIGNED": "dim_aligned",
            "DIMRADIUS": "dim_radius",
            "DIMDIAMETER": "dim_diameter",
            "DIMANGULAR": "dim_angular",
            "M": "move", "MOVE": "move",
            "CO": "copy", "COPY": "copy",
            "RO": "rotate", "ROTATE": "rotate",
            "E": "delete", "ERASE": "delete",
            "Z": "zoom_extents", "ZOOM": "zoom_extents",
            "U": "undo", "UNDO": "undo",
            "REDO": "redo",
            "SAVE": "save", "OPEN": "open",
            "Q": "quit", "QUIT": "quit",
            "X": "explode", "EXPLODE": "explode",
            "O": "offset", "OFFSET": "offset",
            "B": "break", "BREAK": "break",
            "H": "hatch", "HATCH": "hatch",
            "SC": "scale", "SCALE": "scale",
            "MI": "mirror", "MIRROR": "mirror",
            "TR": "trim", "TRIM": "trim",
            "EX": "extend", "EXTEND": "extend",
            "F": "fillet", "FILLET": "fillet",
            "CHA": "chamfer", "CHAMFER": "chamfer",
            "AR": "array", "ARRAY": "array",
            "CLAYER": "clayer",
            "SETVAR": "setvar",
            "TEXTSCR": "textscr",
            "GRAPHSCR": "graphscr",
            "LAYER": "layer_list",
            "COLOR": "color_cmd",
            "COLOUR": "color_cmd",
            "ABOUT": "about",
            "HELP": "help",
            "SNAP": "snap_toggle",
            "ORTHO": "ortho_toggle",
            "GRID": "grid_toggle_cmd",
            "DXFIN": "dxfin_cmd",
            "PLOT": "plot_cmd",
            "PRINT": "plot_cmd",
            "HATCH": "hatch",
            "LINETYPE": "linetype_cmd",
            "LTYPE": "linetype_cmd",
            "TEMPLATE": "layer_template",
            "UNITS": "units_cmd",
            "BLOCK": "block_cmd",
            "INSERT": "insert_cmd",
            "DOOR": "door_cmd",
            "WINDOW": "win_cmd",
        }
        action = aliases.get(cmd)
        if not action:
            self._echo(f"Unknown command: {cmd}")
            self._echo("Command:")
            return

        if action == "zoom_extents":
            self._view.zoom_extents()
            self._echo("Command:")
        elif action == "undo":
            self._on_undo()
            self._echo("Command:")
        elif action == "redo":
            self._on_redo()
            self._echo("Command:")
        elif action == "save":
            self._on_save()
            self._echo("Command:")
        elif action == "open":
            self._on_open()
            self._echo("Command:")
        elif action == "quit":
            self.close()
        elif action == "clayer":
            self._cmd_clayer(args)
            return
        elif action == "setvar":
            self._cmd_setvar(args)
            return
        elif action == "textscr":
            self._text_screen_on()
            self._echo("Command:")
            return
        elif action == "graphscr":
            self._text_screen_off()
            self._echo("Command:")
            return
        elif action == "layer_list":
            self._cmd_layer_list()
            return
        elif action == "color_cmd":
            self._cmd_color(args)
            return
        elif action == "about":
            self._on_about()
            self._echo("Command:")
            return
        elif action == "help":
            self._cmd_help()
            return
        elif action == "snap_toggle":
            self._toggle_snap()
            self._echo(f"Snap {'ON' if self._snap_active else 'OFF'}")
            self._echo("Command:")
            return
        elif action == "ortho_toggle":
            self._toggle_ortho()
            self._echo(f"Ortho {'ON' if self._ortho_active else 'OFF'}")
            self._echo("Command:")
            return
        elif action == "grid_toggle_cmd":
            self._grid.setVisible(not self._grid.isVisible())
            self._echo(f"Grid {'ON' if self._grid.isVisible() else 'OFF'}")
            self._echo("Command:")
            return
        elif action == "dxfin_cmd":
            self._cmd_dxfin()
            return
        elif action == "plot_cmd":
            self._cmd_plot(args)
            return
        elif action == "linetype_cmd":
            self._cmd_linetype(args)
            return
        elif action == "dim_aligned":
            self._tool_manager._aligned_dim = True
            self._activate_tool("dim")
            return
        elif action == "dim_radius":
            self._tool_manager._dim_type = "radius"
            self._activate_tool("dimradius")
            return
        elif action == "dim_diameter":
            self._tool_manager._dim_type = "diameter"
            self._activate_tool("dimradius")
            return
        elif action == "dim_angular":
            self._tool_manager._dim_type = "angular"
            self._activate_tool("dimradius")
            return
        elif action == "layer_template":
            self._cmd_layer_template()
            self._echo("Command:")
            return
        elif action == "units_cmd":
            self._cmd_units(args)
            return
        elif action == "block_cmd":
            self._cmd_block(args)
            return
        elif action == "insert_cmd":
            self._cmd_insert(args)
            return
        elif action == "door_cmd":
            self._cmd_library("DOOR", args)
            return
        elif action == "win_cmd":
            self._cmd_library("WINDOW", args)
            return
        elif action in self._tool_manager._tools:
            self._activate_tool(action)
        else:
            self._echo(f"Unknown command: {cmd}")
            self._echo("Command:")

    # ── SETVAR / CLAYER commands ──────────────────────────
    def _cmd_clayer(self, args: str):
        """CLAYER command: show or set current layer."""
        sv = self._document.sysvars
        if not args:
            val, _ = sv.setvar("CLAYER")
            self._echo(f"Current layer: {val}")
            self._echo("Command:")
            return
        try:
            layer_name = args.strip()
            sv["CLAYER"] = layer_name
            # Sync with LayerManager
            lm = self._document.layer_manager
            if layer_name not in lm.layers:
                lm.add_layer(layer_name)
            lm.set_current(layer_name)
            self._echo(f"CLAYER set to {layer_name}")
            self._echo("Command:")
        except (KeyError, ValueError, TypeError) as e:
            self._echo(f"Invalid layer name: {args}")

    def _cmd_setvar(self, args: str):
        """SETVAR command: list/query/set system variables."""
        sv = self._document.sysvars
        parts = args.strip().split(None, 1)
        if not parts:
            self._echo("SETVAR: Variable name or ?:")
            return

        name = parts[0].upper()
        if name == "?":
            pattern = parts[1].strip() if len(parts) > 1 else "*"
            for vname, val, ro in sv.list_vars(pattern):
                tag = " (read only)" if ro else ""
                if isinstance(val, float):
                    self._echo(f"{vname:<12} {val:.4f}{tag}")
                else:
                    self._echo(f"{vname:<12} {val}{tag}")
            self._echo("Command:")
            return

        if len(parts) == 1:
            # Show value
            try:
                val, ro = sv.setvar(name)
                tag = " (read only)" if ro else ""
                if isinstance(val, float):
                    self._echo(f"{name} = {val:.4f}{tag}")
                else:
                    self._echo(f"{name} = {val}{tag}")
                self._echo("Command:")
            except KeyError:
                self._echo(f"Unknown system variable: {name}")
                self._echo("Command:")
            return

        # Set value
        try:
            sv.setvar_set(name, parts[1])
            val = sv[name]
            # Sync CLAYER with LayerManager
            if name == "CLAYER":
                lm = self._document.layer_manager
                layer_name = str(val)
                if layer_name not in lm.layers:
                    lm.add_layer(layer_name)
                lm.set_current(layer_name)
            if name == "ORTHOMODE":
                self._ortho_active = bool(int(val))
            if isinstance(val, float):
                self._echo(f"{name} = {val:.4f}")
            else:
                self._echo(f"{name} = {val}")
            self._echo("Command:")
        except (KeyError, ValueError, TypeError) as e:
            self._echo(f"SETVAR error: {e}")
            self._echo("Command:")

    def _toggle_text_screen(self):
        """F2: toggle between drawing area and expanded text screen."""
        if not hasattr(self, '_text_screen_active'):
            self._text_screen_active = False
        if self._text_screen_active:
            self._text_screen_off()
        else:
            self._text_screen_on()

    def _text_screen_on(self):
        """Show expanded text screen (hide drawing area)."""
        self._text_screen_active = True
        self._view.hide()
        self._cmd_output.setFixedHeight(self.height() - 100)
        self._echo("── TEXT SCREEN (TEXTSCR / F2 to return) ──")

    def _text_screen_off(self):
        """Return to drawing area (hide text screen)."""
        self._text_screen_active = False
        self._view.show()
        self._cmd_output.setFixedHeight(80)

    def _cmd_layer_list(self):
        """LAYER command: list all layers with status."""
        lm = self._document.layer_manager
        self._echo(f"Current layer: {lm.current_layer_name}")
        self._echo(f"{'Layer name':<20} {'Color':<15} {'State':<20}")
        self._echo("-" * 55)
        for name in sorted(lm.layers):
            layer = lm.layers[name]
            marker = ">" if name == lm.current_layer_name else " "
            # Show ACI color human-friendly
            from src.model.aci import color_to_display, parse_color
            color_display = color_to_display(parse_color(layer.color))
            state = []
            if layer.visible:
                state.append("ON")
            else:
                state.append("OFF")
            if layer.locked:
                state.append("LOCKED")
            self._echo(f"{marker}{name:<19} {color_display:<15} {' '.join(state)}")
        self._echo(f"Total layers: {len(lm.layers)}")
        self._echo("Command:")

    def _cmd_color(self, args: str):
        """COLOR command: show/set current entity color (ACI 1-255)."""
        from src.model.aci import aci_to_hex, aci_to_rgb, parse_color, color_to_display, COLOR_NAMES
        sv = self._document.sysvars
        if not args:
            val = sv["CECOLOR"]
            self._echo(f"Current entity color: {color_to_display(parse_color(val))}")
            self._echo("Command:")
            return
        try:
            idx = parse_color(args)
            sv["CECOLOR"] = str(idx)
            r, g, b = aci_to_rgb(idx)
            name = COLOR_NAMES.get(idx, "")
            self._echo(f"COLOR set to {idx} ({name})  RGB={r},{g},{b}  {aci_to_hex(idx)}")
            self._echo("Command:")
        except (ValueError, KeyError) as e:
            self._echo(f"Invalid color: {args}")
            self._echo("Command:")

    def _cmd_help(self):
        """HELP command: open documentation in Safari."""
        import subprocess
        from pathlib import Path
        doc_path = Path(__file__).parent.parent.parent.parent / "docs" / "index.html"
        if doc_path.exists():
            subprocess.run(["open", "-a", "Safari", str(doc_path)])
            self._echo("Opening documentation in Safari...")
        else:
            self._echo("Documentation not found.")
        self._echo("Command:")

    def _cmd_units(self, args: str):
        """UNITS command: show/set drawing units."""
        from src.model.units import set_units, format_distance, DECIMAL, METRIC_M, METRIC_CM, METRIC_MM, ARCHITECTURAL
        sv = self._document.sysvars
        
        if not args:
            lunits = int(sv["LUNITS"])
            luprec = int(sv["LUPREC"])
            names = {2: "Decimal", 3: "Engineering", 4: "Architectural", 5: "Metric (m)", 6: "Metric (cm)", 7: "Metric (mm)"}
            self._echo(f"Units: {names.get(lunits, str(lunits))}, {luprec} decimals")
            self._echo(f"Options: 2=Decimal 3=Engineering 4=Architectural 5=Metric(m) 6=Metric(cm) 7=Metric(mm)")
        else:
            parts = args.upper().split()
            try:
                lunits = int(parts[0])
                luprec = int(parts[1]) if len(parts) > 1 else 2
                msg = set_units(sv, lunits, luprec)
                self._echo(f"Units: {msg}")
            except ValueError:
                # Named: "METRIC M", "METRIC CM"
                mapping = {"M": METRIC_M, "CM": METRIC_CM, "MM": METRIC_MM, "ARCH": ARCHITECTURAL, "DEC": DECIMAL}
                key = parts[0] if parts else ""
                if key in mapping:
                    msg = set_units(sv, mapping[key])
                    self._echo(f"Units: {msg}")
                else:
                    self._echo(f"Unknown units: {args}")
        self._echo("Command:")

    def _cmd_block(self, args: str):
        """BLOCK command: create a block from selected entities."""
        from PySide6.QtWidgets import QInputDialog
        from src.model.entities.block import BlockDefinition
        
        uuids = self._view._selected_uuids if hasattr(self._view, '_selected_uuids') else []
        if not uuids:
            self._echo("BLOCK: Select entities first (click them)")
            self._echo("Command:")
            return
        
        name = args.strip()
        if not name:
            name, ok = QInputDialog.getText(self, "Block Name", "Block name:")
            if not ok or not name:
                self._echo("BLOCK cancelled.")
                self._echo("Command:")
                return
        
        entities = [self._document._entities[u] for u in uuids if u in self._document._entities]
        if not entities:
            self._echo("BLOCK: No valid entities selected")
            self._echo("Command:")
            return
        
        # Base point = center of selection bounding box
        xs = []
        ys = []
        for e in entities:
            bmin, bmax = e.bounding_box()
            xs.extend([bmin.x, bmax.x])
            ys.extend([bmin.y, bmax.y])
        from src.model.entities.base import Point
        bp = Point(sum(xs) / len(xs), sum(ys) / len(ys))
        
        self._document.block_defs[name] = BlockDefinition(name, entities, bp)
        self._echo(f"BLOCK \"{name}\" created with {len(entities)} entities")
        self._echo("Command:")

    def _cmd_insert(self, args: str):
        """INSERT command: place a block instance."""
        from PySide6.QtWidgets import QInputDialog
        from src.model.entities.block import BlockInstance
        from src.model.entities.base import Point
        
        block_names = list(self._document.block_defs.keys())
        if not block_names:
            self._echo("INSERT: No blocks defined. Use BLOCK first.")
            self._echo("Command:")
            return
        
        name = args.strip()
        if not name or name not in block_names:
            name, ok = QInputDialog.getItem(self, "Insert Block", "Block:", block_names, 0, False)
            if not ok:
                self._echo("INSERT cancelled.")
                self._echo("Command:")
                return
        
        # Use last point or 0,0
        try:
            lp_str = self._document.sysvars["LASTPOINT"]
            parts = lp_str.split(',')
            pt = Point(float(parts[0]), float(parts[1]))
        except Exception:
            pt = Point(0, 0)
        
        inst = BlockInstance(name, pt, layer_name=self._document.layer_manager.current_layer_name)
        self._document.add_entity(inst)
        self._rebuild_scene()
        self._echo(f"INSERT \"{name}\" at {pt.x:.2f}, {pt.y:.2f}")
        self._echo("Command:")

    def _cmd_library(self, elem_type: str, args: str):
        """Create a library element (door/window) and insert it."""
        from src.model.entities.line import Line
        from src.model.entities.circle import Circle
        from src.model.entities.arc import Arc
        from src.model.entities.base import Point
        from src.model.entities.block import BlockDefinition, BlockInstance
        import math
        
        # Determine size from args or default
        size = 0.9  # default 90cm
        if args:
            try:
                size = float(args)
            except ValueError:
                pass
        
        if elem_type == "DOOR":
            name = "DOOR_90"
            if name not in self._document.block_defs:
                # Door: arc + line, 90cm wide, opens counterclockwise
                ents = [
                    Line(Point(0, 0), Point(size, 0)),  # door panel
                    Arc(Point(0, 0), Point(size, 0), Point(size / 2, size / 2)),  # swing arc
                ]
                self._document.block_defs[name] = BlockDefinition(name, ents, Point(0, 0))
                self._echo(f"Library: {name} created")
        elif elem_type == "WINDOW":
            name = f"WINDOW_{int(size*100)}"
            if name not in self._document.block_defs:
                ents = [
                    Line(Point(0, 0), Point(size, 0)),
                    Line(Point(0, 0.1), Point(size, 0.1)),  # frame thickness
                    Line(Point(size/2, 0), Point(size/2, 0.1)),  # mullion
                ]
                self._document.block_defs[name] = BlockDefinition(name, ents, Point(0, 0))
                self._echo(f"Library: {name} created")
        
        # Insert at last point
        try:
            lp_str = self._document.sysvars["LASTPOINT"]
            parts = lp_str.split(',')
            pt = Point(float(parts[0]), float(parts[1]))
        except Exception:
            pt = Point(0, 0)
        
        inst = BlockInstance(name, pt, layer_name=self._document.layer_manager.current_layer_name)
        self._document.add_entity(inst)
        self._rebuild_scene()
        self._echo(f"{elem_type} inserted at {pt.x:.2f}, {pt.y:.2f}")
        self._echo("Command:")

    def _cmd_linetype(self, args: str):
        """LINETYPE command: list or set current entity linetype."""
        from src.model.linetype_defs import list_linetypes, get_linetype
        sv = self._document.sysvars
        if not args:
            lt = sv["CELTYPE"]
            ltdef = get_linetype(lt)
            self._echo(f"Current linetype: {lt} ({ltdef.description})")
            self._echo(f"LTSCALE = {sv['LTSCALE']}")
            self._echo("Use LINETYPE ? to list all")
            self._echo("Command:")
            return
        if args.strip() == "?":
            self._echo("Available linetypes:")
            for name in list_linetypes():
                ltdef = get_linetype(name)
                marker = ">" if name == sv["CELTYPE"] else " "
                self._echo(f"  {marker} {name:<14} {ltdef.description}")
            self._echo("Command:")
            return
        # Set linetype
        name = args.strip().upper()
        try:
            ltdef = get_linetype(name)
            sv["CELTYPE"] = name
            self._echo(f"LINETYPE set to {name} ({ltdef.description})")
            self._echo("Command:")
        except Exception:
            self._echo(f"Unknown linetype: {name}")
            self._echo("Command:")

    def _cmd_layer_template(self):
        """Create standard architectural layer template."""
        from src.model.aci import aci_to_hex
        lm = self._document.layer_manager
        sv = self._document.sysvars
        template = [
            ("0",          "7",    "CONTINUOUS"),   # default
            ("MUROS",      "4",    "CONTINUOUS"),   # cyan
            ("PUERTAS",    "2",    "CONTINUOUS"),   # yellow
            ("VENTANAS",   "3",    "CONTINUOUS"),   # green
            ("COTAS",      "1",    "CONTINUOUS"),   # red
            ("TEXTO",      "7",    "CONTINUOUS"),   # white
            ("EJES",       "1",    "CENTER"),       # red, center linetype
            ("MOBILIARIO", "8",    "CONTINUOUS"),   # dark gray
            ("ELECTRICO",  "5",    "CONTINUOUS"),   # blue
            ("SANITARIO",  "6",    "CONTINUOUS"),   # magenta
            ("CUBIERTA",   "2",    "DASHED"),       # yellow dashed
            ("OCULTO",     "8",    "HIDDEN"),       # gray hidden
        ]
        count = 0
        for name, aci, ltype in template:
            if name not in lm.layers:
                lm.add_layer(name, color=aci)
                if ltype != "CONTINUOUS":
                    pass  # layer doesn't store linetype yet
                count += 1
                self._echo(f"  Created layer: {name} (ACI {aci})")
        self._echo(f"Template loaded: {count} layers")
        sv["CLAYER"] = "0"
        lm.set_current("0")

    def _cmd_dxfin(self):
        """DXFIN command: import DXF file via file dialog."""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        from src.io.dxf_import import import_dxf

        path, _ = QFileDialog.getOpenFileName(
            self, "Import DXF", "", "DXF Files (*.dxf);;All Files (*)")
        if not path:
            self._echo("DXFIN cancelled.")
            self._echo("Command:")
            return

        try:
            count = import_dxf(Path(path), self._document)
            self._echo(f"DXFIN: {count} entities imported from {Path(path).name}")
            self._rebuild_scene()
            self._view.zoom_extents()
        except Exception as e:
            self._echo(f"DXFIN error: {e}")
        self._echo("Command:")

    def _cmd_plot(self, args: str):
        """PLOT command: export viewport to PDF."""
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        from PySide6.QtPrintSupport import QPrinter, QPageSize
        from PySide6.QtGui import QPainter, QColor
        from PySide6.QtCore import QRectF, Qt
        from pathlib import Path

        # Paper sizes in mm (A-series)
        paper_sizes = {
            "A4": (210, 297), "A3": (297, 420), "A2": (420, 594),
            "A1": (594, 841), "A0": (841, 1189),
        }
        scales = ["Fit to paper", "1:1", "1:10", "1:20", "1:50", "1:100", "1:200", "1:500"]

        # Choose scale
        scale_str, ok = QInputDialog.getItem(
            self, "Plot Scale", "Scale:", scales, 4, False)
        if not ok:
            self._echo("PLOT cancelled.")
            self._echo("Command:")
            return

        # Choose paper
        paper_names = list(paper_sizes.keys())
        paper_str, ok = QInputDialog.getItem(
            self, "Paper Size", "Paper:", paper_names, 0, False)
        if not ok:
            self._echo("PLOT cancelled.")
            self._echo("Command:")
            return

        # Choose output file
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", str(Path.home() / "Desktop" / "drawing.pdf"),
            "PDF Files (*.pdf)")
        if not path:
            self._echo("PLOT cancelled.")
            self._echo("Command:")
            return

        try:
            pw_mm, ph_mm = paper_sizes[paper_str]
            pw = int(pw_mm * 2.8346)
            ph = int(ph_mm * 2.8346)

            # Get current viewport scene rect
            vr = self._view.viewport().rect()
            scene_rect = self._view.mapToScene(vr).boundingRect()

            # Calculate scale
            if scale_str == "Fit to paper":
                sw, sh = scene_rect.width(), scene_rect.height()
                scale = min(pw / sw, ph / sh) if sw > 0 and sh > 0 else 1
            else:
                ratio = float(scale_str.split(":")[1])
                scale = pw / (scene_rect.width() * ratio) if scene_rect.width() > 0 else 1

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageSize(QPrinter.PageSize.A4)

            painter = QPainter()
            if not painter.begin(printer):
                self._echo("PLOT error: Cannot start printer")
                self._echo("Command:")
                return

            # White background
            painter.fillRect(printer.pageRect(QPrinter.Unit.DevicePixel),
                           QColor("#FFFFFF"))

            # Render scene centered
            painter.save()
            painter.translate(pw / 2, ph / 2)
            painter.scale(scale, -scale)
            painter.translate(-scene_rect.center().x(), -scene_rect.center().y())
            self._scene.render(painter, QRectF(scene_rect), QRectF(scene_rect))
            painter.restore()
            painter.end()

            self._echo(f"PLOT: {Path(path).name} ({paper_str}, {scale_str})")
            import subprocess
            subprocess.run(["open", path])
        except Exception as e:
            self._echo(f"PLOT error: {e}")
        self._echo("Command:")

    # ── Coord Status Update ───────────────────────────────
    def _update_coord_status(self, scene_pos: QPointF):
        x, y = scene_pos.x(), scene_pos.y()
        from src.model.units import format_distance
        try:
            fx = format_distance(x, self._document.sysvars).replace(" m", "").replace(" cm", "").replace(" mm", "")
            fy = format_distance(y, self._document.sysvars).replace(" m", "").replace(" cm", "").replace(" mm", "")
            self._sb_coords.setText(f"X={fx:>10}  Y={fy:>10}")
        except Exception:
            self._sb_coords.setText(f"X={x:10.4f}  Y={y:10.4f}")
        self._sb_layer.setText(f"LAYER:{self._document.layer_manager.current_layer_name}")
        self._sb_ortho.setText("ORTHO" if self._ortho_active else "")
        # Color from CECOLOR
        try:
            cec = self._document.sysvars["CECOLOR"]
            from src.model.aci import parse_color, COLOR_NAMES
            idx = parse_color(cec)
            name = COLOR_NAMES.get(idx, str(idx))
            self._sb_color.setText(f"COLOR:{name}")
        except Exception:
            self._sb_color.setText("COLOR:White")
        # Linetype from CELTYPE
        try:
            lt = self._document.sysvars["CELTYPE"]
            self._sb_ltype.setText(f"LINETYPE:{lt}")
        except Exception:
            self._sb_ltype.setText("LINETYPE:Continuous")
        # File name
        if self._filename:
            self._sb_file.setText(f"🐾 {self._filename.name}")
        else:
            self._sb_file.setText("🐾 NEW")

    def _toggle_snap(self):
        self._snap_active = not self._snap_active
        self._snap_action.setChecked(self._snap_active)
        self._sb_snap.setText("SNAP" if self._snap_active else "")
        # Toggle active snaps on current tool
        if self._tool_manager._active_tool:
            from src.model.snap import SnapType
            if self._snap_active:
                self._tool_manager._active_tool._active_snaps = {
                    SnapType.ENDPOINT, SnapType.MIDPOINT,
                    SnapType.CENTER, SnapType.NEAREST,
                }
            else:
                self._tool_manager._active_tool._active_snaps = set()

    def _toggle_ortho(self):
        self._ortho_active = not self._ortho_active
        self._ortho_action.setChecked(self._ortho_active)
        self._sb_ortho.setText("ORTHO" if self._ortho_active else "")

    # ── Edit actions ───────────────────────────────────────
    def _on_erase(self):
        uuids = list(self._view._selected_uuids) if hasattr(self._view, '_selected_uuids') else []
        for uuid in uuids:
            if uuid in self._document._entities:
                self._document.remove_entity(uuid)
        for item in list(self._scene.items()):
            if hasattr(item, 'entity') and item.entity.uuid in uuids:
                self._scene.removeItem(item)
        self._view._selected_uuids = []

    def _on_erase_all(self):
        r = QMessageBox.question(self, "Erase All",
                                 "Delete all entities?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            for uuid in list(self._document._entities.keys()):
                self._document.remove_entity(uuid)
            self._rebuild_scene()

    def _on_list_entities(self):
        """List all entities in the command output (INQUIRY menu)."""
        self._echo(f"--- {len(self._document.entities)} ENTITIES ---")
        for e in self._document.entities:
            d = e.to_dict()
            self._echo(f"  {d['type']:10s}  L:{e.layer_name}  uuid:{e.uuid[:8]}")
        self._echo("Command:")

    # ── Layer helpers ───────────────────────────────────────
    def _layer_op(self, op_name: str, fn):
        """Apply an operation to a selected layer."""
        layers = list(self._document.layer_manager.layers.keys())
        name, ok = QInputDialog.getItem(self, f"Layer {op_name}", "Layer:", layers, 0, False)
        if ok and name:
            layer = self._document.layer_manager.layers.get(name)
            if layer:
                fn(layer)
                self._echo(f"Layer {name}: {op_name}")
        self._echo("Command:")

    def _layer_color(self):
        layers = list(self._document.layer_manager.layers.keys())
        name, ok = QInputDialog.getItem(self, "Layer Color", "Layer:", layers, 0, False)
        if ok and name:
            from PySide6.QtWidgets import QColorDialog
            color = QColorDialog.getColor()
            if color.isValid():
                layer = self._document.layer_manager.layers.get(name)
                if layer:
                    layer.color = color.name()
                    self._echo(f"Layer {name}: color={color.name()}")
        self._echo("Command:")

    def _layer_make(self):
        """Make a new layer and set it current (like ACAD LAYER Make)."""
        name, ok = QInputDialog.getText(self, "Make Layer", "New layer name:")
        if ok and name.strip():
            try:
                lm = self._document.layer_manager
                if name.strip() not in lm.layers:
                    lm.add_layer(name.strip())
                lm.set_current(name.strip())
                self._echo(f"Made layer: {name.strip()} (current)")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
        self._echo("Command:")

    def _layer_query(self):
        """List all layers with properties."""
        self._echo("--- LAYERS ---")
        for name, layer in self._document.layer_manager.layers.items():
            cur = ">" if name == self._document.layer_manager.current_layer_name else " "
            vis = "ON" if layer.visible else "OFF"
            lock = "LK" if layer.locked else "UL"
            self._echo(f" {cur} {name:10s} {vis} {lock} {layer.color}")
        self._echo("Command:")

    def _on_id(self):
        """ID command — activate a point-pick to identify entity under cursor."""
        self._activate_tool("id")

    def _on_status(self):
        """STATUS — show drawing statistics."""
        doc = self._document
        ents = doc.entities
        types = {}
        for e in ents:
            t = e.to_dict()["type"]
            types[t] = types.get(t, 0) + 1
        self._echo("--- DRAWING STATUS ---")
        self._echo(f"Entities: {len(ents)}")
        for t, n in sorted(types.items()):
            self._echo(f"  {t:12s}: {n}")
        self._echo(f"Layers: {len(doc.layer_manager.layers)}")
        self._echo(f"Current: {doc.layer_manager.current_layer_name}")
        self._echo(f"Snap: {'ON' if self._snap_active else 'OFF'}")
        self._echo(f"Ortho: {'ON' if self._ortho_active else 'OFF'}")
        self._echo(f"Grid: {'ON' if self._grid.isVisible() else 'OFF'}")
        self._echo("Command:")

    def _on_purge(self):
        """PURGE — remove unused (empty) layers."""
        lm = self._document.layer_manager
        used = {e.layer_name for e in self._document.entities}
        used.add("0")  # never purge layer 0
        purged = []
        for name in list(lm.layers.keys()):
            if name not in used:
                lm.delete_layer(name)
                purged.append(name)
        if purged:
            self._echo(f"Purged layers: {', '.join(purged)}")
        else:
            self._echo("No unused layers to purge.")
        self._echo("Command:")

    def _on_units(self):
        """UNITS — show/set drawing units and precision."""
        from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Drawing Units")
        layout = QVBoxLayout(dlg)

        form = QFormLayout()
        unit_combo = QComboBox()
        unit_combo.addItems(["Decimal", "Engineering", "Architectural", "Fractional", "Scientific"])
        prec_spin = QSpinBox()
        prec_spin.setRange(0, 8)
        prec_spin.setValue(4)
        form.addRow("Units:", unit_combo)
        form.addRow("Precision:", prec_spin)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._echo(f"Units: {unit_combo.currentText()}  Precision: {prec_spin.value()}")
        self._echo("Command:")

    def _on_limits(self):
        """LIMITS — set drawing limits."""
        from PySide6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Drawing Limits")
        layout = QVBoxLayout(dlg)
        form = QFormLayout()

        xmin = QDoubleSpinBox(); xmin.setRange(-100000, 100000); xmin.setValue(-100)
        ymin = QDoubleSpinBox(); ymin.setRange(-100000, 100000); ymin.setValue(-100)
        xmax = QDoubleSpinBox(); xmax.setRange(-100000, 100000); xmax.setValue(100)
        ymax = QDoubleSpinBox(); ymax.setRange(-100000, 100000); ymax.setValue(100)

        form.addRow("Lower-left X:", xmin)
        form.addRow("Lower-left Y:", ymin)
        form.addRow("Upper-right X:", xmax)
        form.addRow("Upper-right Y:", ymax)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            from PySide6.QtCore import QRectF
            from src.view.graphics.grid_item import GridItem
            rect = QRectF(xmin.value(), ymin.value(),
                          xmax.value() - xmin.value(),
                          ymax.value() - ymin.value())
            self._scene.setSceneRect(rect)
            self._scene.removeItem(self._grid)
            self._grid = GridItem(rect, spacing=10.0)
            self._scene.addItem(self._grid)
            self._echo(f"Limits: ({xmin.value():.2f},{ymin.value():.2f}) to ({xmax.value():.2f},{ymax.value():.2f})")
        self._echo("Command:")

    def _on_plot(self):
        """PLOT — print current view."""
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter
        from PySide6.QtGui import QPainter
        printer = QPrinter()
        printer.setPageSize(QPrinter.PageSize.A4)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            self._view.render(painter)
            painter.end()
            self._echo("Plot sent to printer.")
        self._echo("Command:")

    # ── Layer dialog ───────────────────────────────────────
    def _show_layer_dialog(self):
        """Simple layer manager dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Layers")
        dlg.resize(300, 250)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Name", "Color", "Current"])
        for layer in self._document.layer_manager.layers.values():
            cur = ">" if layer.name == self._document.layer_manager.current_layer_name else ""
            item = QTreeWidgetItem([layer.name, layer.color, cur])
            tree.addTopLevelItem(item)

        btn_layout = QHBoxLayout()
        new_btn = QPushButton("New")
        del_btn = QPushButton("Delete")
        set_btn = QPushButton("Set Current")
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(set_btn)

        layout = QVBoxLayout(dlg)
        layout.addWidget(tree)
        layout.addLayout(btn_layout)

        def on_new():
            name, ok = QInputDialog.getText(dlg, "New Layer", "Name:")
            if ok and name.strip():
                try:
                    self._document.layer_manager.add_layer(name.strip())
                    tree.clear()
                    for l in self._document.layer_manager.layers.values():
                        cur = ">" if l.name == self._document.layer_manager.current_layer_name else ""
                        tree.addTopLevelItem(QTreeWidgetItem([l.name, l.color, cur]))
                except ValueError as e:
                    QMessageBox.warning(dlg, "Error", str(e))

        def on_del():
            items = tree.selectedItems()
            if items:
                name = items[0].text(0)
                self._document.layer_manager.delete_layer(name)
                tree.clear()
                for l in self._document.layer_manager.layers.values():
                    cur = ">" if l.name == self._document.layer_manager.current_layer_name else ""
                    tree.addTopLevelItem(QTreeWidgetItem([l.name, l.color, cur]))

        def on_set():
            items = tree.selectedItems()
            if items:
                self._document.layer_manager.set_current(items[0].text(0))
                dlg.accept()

        new_btn.clicked.connect(on_new)
        del_btn.clicked.connect(on_del)
        set_btn.clicked.connect(on_set)

        dlg.exec()

    # ── File operations ────────────────────────────────────
    def _on_new(self):
        if self._document.is_dirty:
            r = QMessageBox.question(self, "Unsaved Changes",
                                     "Discard changes?",
                                     QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if r != QMessageBox.StandardButton.Discard:
                return
        self._document = Document()
        self._filename = None
        self._rebuild_scene()

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Drawing", "",
                                              "DogCAD Files (*.cadlite);;All Files (*)")
        if path:
            self._document = load_document(Path(path))
            self._filename = Path(path)
            self._rebuild_scene()
            self._echo(f"Loaded: {path}")

    def _on_save(self):
        if self._filename:
            save_document(self._document, self._filename)
            self._echo(f"Saved: {self._filename}")
        else:
            self._on_save_as()

    def _on_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Drawing As", "",
                                               "DogCAD Files (*.cadlite);;All Files (*)")
        if path:
            p = Path(path)
            if p.suffix != ".cadlite":
                p = p.with_suffix(".cadlite")
            save_document(self._document, p)
            self._filename = p
            self._echo(f"Saved: {p}")

    def _on_export_dxf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export DXF", "",
                                               "DXF Files (*.dxf);;All Files (*)")
        if path:
            export_dxf(self._document, Path(path))
            self._echo(f"DXF exported: {path}")

    def _on_script(self):
        """SCRIPT — run a .scr command file."""
        path, _ = QFileDialog.getOpenFileName(self, "Run Script", "",
                                               "Script Files (*.scr);;All Files (*)")
        if path:
            from src.io.script_engine import ScriptEngine
            engine = ScriptEngine(
                self._document, self._view,
                self._echo, self._rebuild_scene)
            engine.run(Path(path))

    def _on_about(self):
        """ACERCA DE — psychedelic about dialog."""
        from src.view.ui.psychedelic_about import PsychedelicAbout
        dlg = PsychedelicAbout(self)
        dlg.exec()

    def _on_undo(self):
        self._document.undo()
        self._rebuild_scene()

    def _on_redo(self):
        self._document.redo()
        self._rebuild_scene()

    # ── Scene rebuild ──────────────────────────────────────
    def _rebuild_scene(self):
        for item in list(self._scene.items()):
            if item is not self._grid:
                self._scene.removeItem(item)

        from src.view.graphics.entity_items import (
            GfxLineItem, GfxCircleItem, GfxArcItem,
            GfxPolylineItem, GfxTextItem, GfxDimensionItem,
            GfxPointItem,
        )
        from src.model.entities.line import Line
        from src.model.entities.circle import Circle
        from src.model.entities.arc import Arc
        from src.model.entities.polyline import Polyline
        from src.model.entities.text import TextEntity
        from src.model.entities.dimension import Dimension
        from src.model.entities.point_entity import PointEntity
        from src.model.entities.block import BlockInstance

        for entity in self._document.entities:
            if isinstance(entity, Line):
                item = GfxLineItem(entity)
            elif isinstance(entity, Circle):
                item = GfxCircleItem(entity)
            elif isinstance(entity, Arc):
                item = GfxArcItem(entity)
            elif isinstance(entity, Polyline):
                item = GfxPolylineItem(entity)
            elif isinstance(entity, TextEntity):
                item = GfxTextItem(entity)
            elif isinstance(entity, Dimension):
                item = GfxDimensionItem(entity)
            elif isinstance(entity, Ellipse):
                item = GfxEllipseItem(entity)
            elif isinstance(entity, PointEntity):
                item = GfxPointItem(entity)
            elif isinstance(entity, BlockInstance):
                # Expand block instance into individual entity graphics
                block_def = self._document.block_defs.get(entity.block_name)
                if block_def:
                    for sub_ent in entity.get_transformed_entities(block_def):
                        if isinstance(sub_ent, Line):
                            self._scene.addItem(GfxLineItem(sub_ent))
                        elif isinstance(sub_ent, Circle):
                            self._scene.addItem(GfxCircleItem(sub_ent))
                        elif isinstance(sub_ent, Arc):
                            self._scene.addItem(GfxArcItem(sub_ent))
                        elif isinstance(sub_ent, Polyline):
                            self._scene.addItem(GfxPolylineItem(sub_ent))
                continue
            else:
                continue
            self._scene.addItem(item)

        self._init_tools()

    def keyPressEvent(self, event):
        """Global ESC handler — focus command line regardless of widget focus."""
        if event.key() == Qt.Key.Key_Escape:
            if hasattr(self, '_cmd_input'):
                self._cmd_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                self._cmd_input.setFocus()
                self._cmd_input.raise_()
                self._cmd_input.setCursorWidth(3)
            event.accept()
            return
        super().keyPressEvent(event)
