# DogCAD 2D Lite 🔥🐾

> *"Si AutoCAD R10 y Python tuvieran un hijo en Zipaquirá"*

Desktop 2D CAD hecho en **Zipaquirá, Cundinamarca 🇨🇴** con Python, PySide6, ezdxf, y puro vicio. Interfaz retro AutoCAD 10 (1988) — screen menu azul VGA, línea de comandos con historial, coordenadas Y+ arriba, ACI 256 colores, 11 modos OSNAP, engine SETVAR, y un pug de icono.

---

## ⚡ Quick Start

```bash
git clone https://github.com/gcorrea2005/cad2d-lite.git
cd cad2d-lite
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

---

## 🎨 Features

| Categoría | Tools |
|-----------|-------|
| **Draw** | LINE, ARC, CIRCLE, PLINE, RECTANG, TEXT, DIM, POINT, HATCH, SOLID |
| **Modify** | ERASE, MOVE, COPY, ROTATE, MIRROR, SCALE, OFFSET, TRIM, EXTEND, FILLET, CHAMFER, BREAK, EXPLODE, ARRAY |
| **Display** | ZOOM E, ZOOM W, ZOOM P, PAN, REDRAW, REGEN |
| **Inquiry** | DIST, AREA, ID, LIST |
| **Layers** | LAYER, CLAYER, MAKE, SET, NEW, ON, OFF, COLOR, FREEZE, THAW, LOCK, UNLOCK, DELETE |
| **Snaps** | END, MID, CEN, NOD, QUA, INT, INS, PER, TAN, NEA, QUI (11 modos ACAD R10) |
| **SETVAR** | 43 system variables (OSMODE, PDMODE, PDSIZE, CECOLOR, FILLETRAD, DIMSCALE...) |
| **Colors** | ACI 256-color palette (AutoCAD Color Index) |
| **Cursor** | Full-screen crosshair + pickbox verde 8px |
| **I/O** | .cadlite (JSON), DXF export (ezdxf), SCRIPT (.scr) |
| **Undo** | Command pattern, undo/redo ilimitado |

---

## ⌨️ Commands

```
LINE 0,0 10,5          Draw line
CIRCLE 5,5 3           Draw circle
RECTANG 0,0 10,5       Draw rectangle
COLOR 1                Set current color (1=Red, 2=Yellow, 3=Green...)
CLAYER walls           Set current layer
LAYER                  List all layers
SETVAR OSMODE 35       Set running OSNAP (END+MID+INT+NEA)
SETVAR PDMODE 35       Point style: X with circle
SETVAR PDSIZE 2        Point size: 2 units
HELP                   Open documentation in Safari
ABOUT                  Psychedelic about dialog
TEXTSCR / GRAPHSCR     Toggle text screen (F2)
SNAP / ORTHO           Toggle snap/ortho (also F9/F8)
ZOOM E                 Zoom extents
UNDO / REDO            (Ctrl+Z / Ctrl+Y)
SAVE / OPEN            File operations
```

---

## ⌨️ Keyboard Shortcuts

| Tecla | Acción |
|-------|--------|
| `L` `C` `A` `P` `R` `T` `D` `M` `O` `X` | Tools |
| `Esc` | Cancel tool → command line |
| `F2` | Text screen toggle |
| `F8` | Ortho toggle |
| `F9` | Snap toggle |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `↑` / `↓` | Command history |

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 74 passed
```

---

## 🗂️ Project Structure

```
src/
├── model/          # Entidades, capas, snap engine, ACI palette, SETVAR, document
│   ├── aci.py          # AutoCAD Color Index (256 colors)
│   ├── sysvars.py      # 43 system variables (SETVAR engine)
│   └── snap.py         # 11 OSNAP modes with priority
├── view/           # Qt GUI, CadView, CrosshairOverlay, GfxItems, pug icon
├── controller/     # 30 herramientas + command pattern
├── io/             # .cadlite JSON, DXF export, SCRIPT engine
└── main.py         # Entry point
tests/              # 74 pytest tests
scripts/            # Demo: generate_apto.py, apto_66m2.scr
docs/               # HTML documentation (open with HELP command)
```

---

## 🎨 Retro UI Colors

| Elemento | Color |
|----------|-------|
| Screen menu | `#0000AA` (VGA blue) |
| Grid | `#0a1a2a` |
| Text | `#FFFFFF` |
| Headers | `#44AAFF` |
| Status bar | `#000088` |
| Accent | `#FFCC00` |
| Crosshair | White (alpha 180) |
| Pickbox | `#00FF00` (green) |
| Cursor | `#00FF00` (green blink) |

---

## 🧠 Tech Stack

`Python 3.12` · `PySide6 6.11` · `ezdxf 1.1` · `pytest 9.1`

---

## 👨‍💻 Autor

**Giovanni Correa** — Ingeniero civil, Zipaquirá, Cundinamarca.
Hecho con Python, vicio, y pan de sagú.
Dedicado a la memoria de AutoCAD R10 (1988) — DOS, EGA/VGA.

---

## 📜 Licencia

MIT — dibuje sin miedo.
