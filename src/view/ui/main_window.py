from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QToolBar, QStatusBar, QDockWidget,
    QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QInputDialog, QFileDialog, QMessageBox,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, QPointF
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
        self._setup_toolbar()
        self._setup_layer_panel()
        self._setup_command_line()
        self._setup_statusbar()

    def _init_scene(self):
        self._scene = CadScene()
        self._view = CadView(self._scene)
        self.setCentralWidget(self._view)

        self._grid = GridItem(self._scene.sceneRect(), spacing=10.0)
        self._scene.addItem(self._grid)

        self._view._status_callback = self._update_coord_status

    def _init_tools(self):
        lm = self._document.layer_manager
        d = self._document
        v = self._view
        self._tool_manager = ToolManager(v, d)

        # Draw tools
        self._tool_manager.register_tool("select", SelectTool(v, d))
        self._tool_manager.register_tool("line", LineTool(v, d, lm))
        self._tool_manager.register_tool("circle", CircleTool(v, d, lm))
        self._tool_manager.register_tool("arc", ArcTool(v, d, lm))
        self._tool_manager.register_tool("polyline", PolylineTool(v, d, lm))
        self._tool_manager.register_tool("rectangle", RectangleTool(v, d, lm))
        self._tool_manager.register_tool("text", TextTool(v, d, lm))
        self._tool_manager.register_tool("dim", DimLinearTool(v, d, lm))

        # Modify tools
        self._tool_manager.register_tool("move", MoveTool(v, d))
        self._tool_manager.register_tool("copy", CopyTool(v, d))
        self._tool_manager.register_tool("rotate", RotateTool(v, d))
        self._tool_manager.register_tool("delete", DeleteTool(v, d))

        self._view.tool_manager = self._tool_manager
        self._tool_manager.activate_tool("select")

    def _setup_menus(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("&File")
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        dxf_action = QAction("Export &DXF...", self)
        dxf_action.triggered.connect(self._on_export_dxf)
        file_menu.addAction(dxf_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = mb.addMenu("&Edit")
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_action)

    def _setup_toolbar(self):
        draw_tb = QToolBar("Draw")
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, draw_tb)

        def add_tool_btn(text, shortcut, tool_name):
            action = QAction(text, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(lambda _n=tool_name: self._tool_manager.activate_tool(_n))
            draw_tb.addAction(action)

        # Select (escape)
        sel_action = QAction("Select", self)
        sel_action.setShortcut(QKeySequence("Esc"))
        sel_action.triggered.connect(lambda: self._tool_manager.activate_tool("select"))
        draw_tb.addAction(sel_action)

        draw_tb.addSeparator()
        add_tool_btn("Line", "L", "line")
        add_tool_btn("Circle", "C", "circle")
        add_tool_btn("Arc", "A", "arc")
        add_tool_btn("Polyline", "P", "polyline")
        add_tool_btn("Rectangle", "R", "rectangle")
        add_tool_btn("Text", "T", "text")
        add_tool_btn("Dim", "D", "dim")

        draw_tb.addSeparator()
        add_tool_btn("Move", "M", "move")
        add_tool_btn("Copy", "Ctrl+C", "copy")
        add_tool_btn("Rotate", "Ctrl+R", "rotate")
        add_tool_btn("Delete", "Del", "delete")

    def _setup_layer_panel(self):
        dock = QDockWidget("Layers", self)
        self._layer_tree = QTreeWidget()
        self._layer_tree.setHeaderLabels(["Name", "Color", "Visible"])
        self._layer_tree.setColumnCount(3)

        btn_widget = QWidget()
        btn_layout = QVBoxLayout(btn_widget)
        add_btn = QPushButton("Add Layer")
        add_btn.clicked.connect(self._on_add_layer)
        del_btn = QPushButton("Delete Layer")
        del_btn.clicked.connect(self._on_delete_layer)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self._layer_tree)
        layout.addWidget(btn_widget)

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self._refresh_layer_panel()

    def _refresh_layer_panel(self):
        self._layer_tree.clear()
        for layer in self._document.layer_manager.layers.values():
            item = QTreeWidgetItem([layer.name, layer.color, "✓" if layer.visible else "✗"])
            item.setData(0, Qt.ItemDataRole.UserRole, layer.name)
            if layer.name == self._document.layer_manager.current_layer_name:
                item.setBackground(0, Qt.GlobalColor.darkBlue)
            self._layer_tree.addTopLevelItem(item)
        self._layer_tree.itemDoubleClicked.connect(self._on_layer_double_click)

    def _on_layer_double_click(self, item, column):
        name = item.data(0, Qt.ItemDataRole.UserRole)
        if name:
            self._document.layer_manager.set_current(name)
            self._refresh_layer_panel()

    def _on_add_layer(self):
        name, ok = QInputDialog.getText(self, "New Layer", "Layer name:")
        if ok and name.strip():
            try:
                self._document.layer_manager.add_layer(name.strip())
                self._refresh_layer_panel()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _on_delete_layer(self):
        items = self._layer_tree.selectedItems()
        if items:
            name = items[0].data(0, Qt.ItemDataRole.UserRole)
            if self._document.layer_manager.delete_layer(name):
                self._refresh_layer_panel()

    def _setup_command_line(self):
        dock = QDockWidget("Command", self)
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText("Type a command (e.g., LINE 0,0 10,10)")
        self._cmd_input.returnPressed.connect(self._on_command)
        dock.setWidget(self._cmd_input)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def _on_command(self):
        text = self._cmd_input.text().strip()
        self._cmd_input.clear()
        if not text:
            return
        parts = text.upper().split()
        cmd = parts[0]
        aliases = {
            "L": "line", "LINE": "line",
            "C": "circle", "CIRCLE": "circle",
            "A": "arc", "ARC": "arc",
            "P": "polyline", "PL": "polyline", "POLYLINE": "polyline",
            "R": "rectangle", "REC": "rectangle", "RECTANGLE": "rectangle",
            "T": "text", "TEXT": "text", "MTEXT": "text",
            "D": "dim", "DIM": "dim", "DIMLINEAR": "dim",
            "M": "move", "MOVE": "move",
            "CO": "copy", "COPY": "copy",
            "RO": "rotate", "ROTATE": "rotate",
            "E": "delete", "ERASE": "delete", "DEL": "delete",
        }
        if cmd in aliases:
            self._tool_manager.activate_tool(aliases[cmd])

    def _setup_statusbar(self):
        self._coord_label = QStatusBar()
        self.setStatusBar(self._coord_label)
        self._coord_label.showMessage("Ready | 0.00, 0.00")

    def _update_coord_status(self, scene_pos: QPointF):
        tool_name = ""
        if self._tool_manager._active_tool:
            tool_name = type(self._tool_manager._active_tool).__name__
        self._coord_label.showMessage(
            f"{tool_name} | {scene_pos.x():.2f}, {scene_pos.y():.2f}  "
            f"Layer: {self._document.layer_manager.current_layer_name}"
        )

    # File operations
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
        self._refresh_layer_panel()

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                              "CAD Lite Files (*.cadlite);;All Files (*)")
        if path:
            self._document = load_document(Path(path))
            self._filename = Path(path)
            self._rebuild_scene()
            self._refresh_layer_panel()

    def _on_save(self):
        if self._filename:
            save_document(self._document, self._filename)
        else:
            self._on_save_as()

    def _on_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "",
                                               "CAD Lite Files (*.cadlite);;All Files (*)")
        if path:
            p = Path(path)
            if p.suffix != ".cadlite":
                p = p.with_suffix(".cadlite")
            save_document(self._document, p)
            self._filename = p

    def _on_export_dxf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export DXF", "",
                                               "DXF Files (*.dxf);;All Files (*)")
        if path:
            export_dxf(self._document, Path(path))

    def _on_undo(self):
        self._document.undo()
        self._rebuild_scene()

    def _on_redo(self):
        self._document.redo()
        self._rebuild_scene()

    def _rebuild_scene(self):
        """Full scene rebuild — clear all entity items and re-add from document."""
        # Remove entity items but keep grid
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

        self._tool_manager = ToolManager(self._view, self._document)
        lm = self._document.layer_manager
        d = self._document
        v = self._view
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
        self._tool_manager.activate_tool("select")
