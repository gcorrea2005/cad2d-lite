#!/usr/bin/env python3
"""Launch DogCAD + auto-run cercha_19vanos.scr after event loop starts."""
import sys, pathlib
from PySide6.QtCore import QTimer
import src.view.ui.main_window as mw
import src.app

_orig_init = mw.MainWindow.__init__

def _init_with_script(self):
    _orig_init(self)
    QTimer.singleShot(0, lambda: self._run_scr(
        pathlib.Path("examples/cercha_19vanos.scr")
    ))

def _run_scr(self, scr_path):
    from src.io.script_engine import ScriptEngine
    engine = ScriptEngine(
        self._document, self._view,
        self._echo, self._rebuild_scene)
    engine.run(scr_path)
    # Force status bar update — layers + coords
    lm = self._document.layer_manager
    self._sb_layer.setText(f"LAYER:{lm.current_layer_name}")
    self._sb_color.setText(f"COLOR:{self._document.sysvars.get('CECOLOR', 'BYLAYER')}")
    self._echo(f"Layers: {list(lm.layers.keys())}")

mw.MainWindow.__init__ = _init_with_script
mw.MainWindow._run_scr = _run_scr

src.app.run()
