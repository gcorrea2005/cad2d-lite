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
from src.controller.tools.select_tool import SelectTool
from src.controller.tools.move_tool import MoveTool
from src.controller.tools.copy_tool import CopyTool
from src.controller.tools.rotate_tool import RotateTool
from src.controller.tools.delete_tool import DeleteTool
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
        self.setWindowTitle("CAD 2D Lite")
        self.resize(1280, 800)

        self._document = Document()
        self._filename: Path | None = None

        self._init_scene()
        self._init_tools()
        self._setup_menus()
        self._setup_screen_menu()
        self._setup_command_line()
        self._setup_statusbar()
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
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 3px 6px;
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
                font-size: 12px;
            }}
            QStatusBar {{
                background-color: {CLR_STATUS_BG};
                color: {CLR_TEXT};
                font-family: 'Courier New', monospace;
                font-size: 11px;
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
                font-size: 11px;
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

        self._view.tool_manager = self._tool_manager
        # Add info toolbar below menus (ACAD 10 style)
        self._info_bar = QToolBar("Info")
        self._info_bar.setMovable(False)
        self._info_bar.setStyleSheet(f"""
            QToolBar {{
                background-color: {CLR_INFO_BG};
                border-bottom: 1px solid #000055;
                spacing: 20px;
                padding: 2px 8px;
            }}
            QLabel {{
                color: {CLR_MENU_TEXT};
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }}
        """)
        self._info_layer = QLabel("LAYER: 0")
        self._info_ortho = QLabel("")
        self._info_coords = QLabel("0.0000, 0.0000")
        self._info_bar.addWidget(self._info_layer)
        self._info_bar.addSeparator()
        self._info_bar.addWidget(self._info_ortho)
        self._info_bar.addSeparator()
        self._info_bar.addWidget(self._info_coords)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._info_bar)

        self._tool_manager.activate_tool("select")

    def _activate_tool(self, name: str):
        """Activate tool and echo command to command line."""
        if name in self._tool_manager._tools:
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
        m.addAction("LINE", lambda: self._activate_tool("line"), "L")
        m.addAction("CIRCLE", lambda: self._activate_tool("circle"), "C")
        m.addAction("ARC", lambda: self._activate_tool("arc"), "A")
        m.addAction("PLINE", lambda: self._activate_tool("polyline"), "P")
        m.addAction("RECTANG", lambda: self._activate_tool("rectangle"), "R")
        m.addAction("TEXT", lambda: self._activate_tool("text"), "T")
        m.addAction("DIM", lambda: self._activate_tool("dim"), "D")

        # Modify
        m = mb.addMenu("MODIFY")
        m.addAction("MOVE", lambda: self._activate_tool("move"), "M")
        m.addAction("COPY", lambda: self._activate_tool("copy"), "Ctrl+Shift+C")
        m.addAction("ROTATE", lambda: self._activate_tool("rotate"), "Ctrl+R")

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

        m.addSeparator()
        m.addAction("LAYERS", self._show_layer_dialog)

    # ── Screen Menu (right side) ───────────────────────────
    def _setup_screen_menu(self):
        dock = QDockWidget("SCREEN MENU", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self._screen_menu = QListWidget()
        self._screen_menu.setFixedWidth(140)
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

        if self._screen_menu_state == "root":
            items = [
                ("* * * *", None),
                ("", None),
                ("  DRAW  ", "menu_draw"),
                ("  EDIT  ", "menu_edit"),
                ("  DISPLAY", "menu_display"),
                ("  LAYER  ", "menu_layer"),
                ("  SETTINGS", "menu_settings"),
                ("", None),
                ("  SAVE   ", "save"),
                ("  OPEN   ", "open"),
                ("  DXF OUT", "dxf"),
                ("", None),
                ("  QUIT   ", "quit"),
            ]
        elif self._screen_menu_state == "menu_draw":
            items = [
                ("  DRAW   ", None),
                ("", None),
                (" LINE    ", "line"),
                (" CIRCLE  ", "circle"),
                (" ARC     ", "arc"),
                (" PLINE   ", "polyline"),
                (" RECTANG ", "rectangle"),
                (" TEXT    ", "text"),
                (" DIM     ", "dim"),
                ("", None),
                (" [<- BACK]", "root"),
            ]
        elif self._screen_menu_state == "menu_edit":
            items = [
                ("  EDIT   ", None),
                ("", None),
                (" ERASE   ", "erase"),
                (" MOVE    ", "move"),
                (" COPY    ", "copy"),
                (" ROTATE  ", "rotate"),
                (" UNDO    ", "undo"),
                (" REDO    ", "redo"),
                ("", None),
                (" [<- BACK]", "root"),
            ]
        elif self._screen_menu_state == "menu_display":
            items = [
                ("  DISPLAY", None),
                ("", None),
                (" ZOOM E  ", "zoom_extents"),
                (" REDRAW  ", "redraw"),
                ("", None),
                (" [<- BACK]", "root"),
            ]
        elif self._screen_menu_state == "menu_layer":
            items = [
                ("  LAYER   ", None),
                ("", None),
                (" SET CUR  ", "layer_set"),
                (" NEW      ", "layer_new"),
                (" DELETE   ", "layer_del"),
                ("", None),
                (" [<- BACK]", "root"),
            ]
        elif self._screen_menu_state == "menu_settings":
            items = [
                ("  SETTINGS", None),
                ("", None),
                (" SNAP  ON ", "snap_toggle"),
                (" ORTHO OFF", "ortho_toggle"),
                (" GRID  ON ", "grid_toggle"),
                ("", None),
                (" [<- BACK]", "root"),
            ]
        else:
            items = []

        for label, action in items:
            if label == "":
                item = QListWidgetItem("")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self._screen_menu.addItem(item)
                continue
            item = QListWidgetItem(label)
            if action:
                item.setData(Qt.ItemDataRole.UserRole, action)
                if label.startswith("[<-"):
                    item.setForeground(QColor("#FFCC00"))  # yellow back
                else:
                    item.setForeground(QColor(CLR_MENU_TEXT))
            else:
                # Header — not clickable, green
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setForeground(QColor(CLR_HEADER))
            self._screen_menu.addItem(item)

    def _on_screen_menu_click(self, item: QListWidgetItem):
        action = item.data(Qt.ItemDataRole.UserRole)
        if not action:
            return

        if action in ("menu_draw", "menu_edit", "menu_display", "menu_layer",
                       "menu_settings", "root"):
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
        elif action == "redraw":
            self._rebuild_scene()
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
        self._cmd_output.setFixedHeight(60)
        self._cmd_output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._cmd_input = QPlainTextEdit()
        self._cmd_input.setFixedHeight(24)
        self._cmd_input.setPlaceholderText("Command:")
        self._cmd_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cmd_input.setTabChangesFocus(False)

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

        self._echo("CAD 2D Lite — Type a command or use screen menu")
        self._echo("Command:")

    def eventFilter(self, obj, event):
        """Capture Enter in command input."""
        from PySide6.QtCore import QEvent
        if obj == self._cmd_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                text = self._cmd_input.toPlainText().strip()
                self._cmd_input.clear()
                if text:
                    self._process_command(text)
                return True
        return super().eventFilter(obj, event)

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
        parts = text.upper().split()
        if not parts:
            return
        cmd = parts[0]
        aliases = {
            "L": "line", "LINE": "line",
            "C": "circle", "CIRCLE": "circle",
            "A": "arc", "ARC": "arc",
            "P": "polyline", "PL": "polyline", "PLINE": "polyline",
            "R": "rectangle", "REC": "rectangle", "RECTANG": "rectangle",
            "T": "text", "TEXT": "text",
            "D": "dim", "DIM": "dim",
            "M": "move", "MOVE": "move",
            "CO": "copy", "COPY": "copy",
            "RO": "rotate", "ROTATE": "rotate",
            "E": "delete", "ERASE": "delete",
            "Z": "zoom_extents", "ZOOM": "zoom_extents",
            "U": "undo", "UNDO": "undo",
            "REDO": "redo",
            "SAVE": "save", "OPEN": "open",
            "Q": "quit", "QUIT": "quit",
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
        elif action in self._tool_manager._tools:
            self._activate_tool(action)
        else:
            self._echo(f"Unknown command: {cmd}")
            self._echo("Command:")

    # ── Status Bar ─────────────────────────────────────────
    def _setup_statusbar(self):
        self._coord_label = QLabel("  0.0000, 0.0000")
        self._layer_label = QLabel("L:0")
        self._snap_label = QLabel("SNAP")
        self._ortho_label = QLabel("")

        sb = QStatusBar()
        sb.addWidget(self._coord_label, 1)
        sb.addWidget(self._layer_label)
        sb.addPermanentWidget(self._snap_label)
        sb.addPermanentWidget(self._ortho_label)
        self.setStatusBar(sb)

    def _update_coord_status(self, scene_pos: QPointF):
        self._info_coords.setText(f"{scene_pos.x():.4f}, {scene_pos.y():.4f}")
        self._info_layer.setText(f"LAYER: {self._document.layer_manager.current_layer_name}")
        self._info_ortho.setText("ORTHO" if self._ortho_active else "")
        self._layer_label.setText(f"L:{self._document.layer_manager.current_layer_name}")

    def _toggle_snap(self):
        self._snap_active = not self._snap_active
        self._snap_action.setChecked(self._snap_active)
        self._snap_label.setText("SNAP" if self._snap_active else "    ")
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
        self._ortho_label.setText("ORTHO" if self._ortho_active else "")

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
                                              "CAD Lite Files (*.cadlite);;All Files (*)")
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
                                               "CAD Lite Files (*.cadlite);;All Files (*)")
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
        )
        from src.model.entities.line import Line
        from src.model.entities.circle import Circle
        from src.model.entities.arc import Arc
        from src.model.entities.polyline import Polyline
        from src.model.entities.text import TextEntity
        from src.model.entities.dimension import Dimension

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
            else:
                continue
            self._scene.addItem(item)

        self._init_tools()
        self._refresh_screen_menu()
