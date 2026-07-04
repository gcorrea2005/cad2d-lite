# CAD 2D Lite

Desktop 2D CAD application — Python + PySide6 + ezdxf.  
Retro AutoCAD 10 style interface. Built in Bogotá 🇨🇴.

## Features
- **30 tools**: LINE, CIRCLE, ARC, PLINE, RECTANG, TEXT, DIM, POINT, HATCH, SOLID
- **Modify**: MOVE, COPY, ROTATE, MIRROR, SCALE, OFFSET, TRIM, EXTEND, FILLET, CHAMFER, BREAK, EXPLODE, ARRAY
- **Display**: ZOOM E/W/P, PAN, REDRAW, REGEN
- **Inquiry**: LIST, DIST, AREA, ID, STATUS
- **Layers**: full management (?, MAKE, SET, NEW, ON, OFF, COLOR, FREEZE, THAW, LOCK, UNLOCK)
- **Snap**: ENDPOINT, MIDPOINT, CENTER, NEAREST (pixel-based tolerance)
- **DXF export** via ezdxf
- **SCRIPT** command (ACAD-style .scr files)
- **Undo/Redo** with command pattern
- **ACAD 10 retro UI**: blue screen menu, info bar, multi-line command history

## Quick Start
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Keyboard Shortcuts
| Key | Tool |
|-----|------|
| L | Line |
| C | Circle |
| A | Arc |
| P | Polyline |
| R | Rectangle |
| T | Text |
| D | Dimension |
| M | Move |
| Esc | Select |
| F8 | Ortho toggle |
| F9 | Snap toggle |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

## Command Line
```
LINE 0,0 10,0
CIRCLE 5,5 3
RECTANG 0,0 10,5
TEXT 5,2 Hello
LAYER NEW walls
ZOOM E
SCRIPT scripts/apto_66m2.scr
```

## Project Structure
```
src/
├── model/          # Entity model, layers, snap engine, document
├── view/           # Qt GUI, scene, graphics items, UI
├── controller/     # 30 tools, command pattern
├── io/             # .cadlite JSON, DXF export, script engine
└── main.py         # Entry point
tests/              # 60 pytest tests
scripts/            # Demo scripts (.scr, generation)
```

## Tech
Python 3.12, PySide6 6.11, ezdxf 1.1, pytest 9.1
