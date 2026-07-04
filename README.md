# CAD 2D Lite 🔥

> *"Si AutoCAD R10 y Python tuvieran un hijo en Zipaquirá"*

Desktop 2D CAD application hecho en **Zipaquirá, Cundinamarca 🇨🇴** con Python, PySide6, ezdxf, y puro vicio. Interfaz retro AutoCAD 10 (1988) — screen menu azul VGA, línea de comandos multilínea, coordenadas Y+ arriba como Dios manda.

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
| **Modify** | MOVE, COPY, ROTATE, MIRROR, SCALE, OFFSET, TRIM, EXTEND, FILLET, CHAMFER, BREAK, EXPLODE, ARRAY |
| **Display** | ZOOM E, ZOOM W, ZOOM P, PAN, REDRAW, REGEN |
| **Inquiry** | LIST, DIST, AREA, ID, STATUS |
| **Layers** | ?, MAKE, SET, NEW, ON, OFF, COLOR, FREEZE, THAW, LOCK, UNLOCK, DELETE |
| **Snaps** | ENDPOINT, MIDPOINT, CENTER, NEAREST |
| **I/O** | .cadlite (JSON), DXF export (ezdxf), SCRIPT (.scr) |
| **Undo** | Command pattern, undo/redo ilimitado |

---

## ⌨️ Keyboard Shortcuts

| Tecla | Tool |
|-------|------|
| `L` | Line |
| `C` | Circle |
| `A` | Arc |
| `P` | Polyline |
| `R` | Rectangle |
| `T` | Text |
| `D` | Dimension |
| `M` | Move |
| `O` | Offset |
| `X` | Explode |
| `Esc` | Select |
| `Supr` | Erase selected |
| `F8` | Ortho toggle |
| `F9` | Snap toggle |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |

---

## 📟 Command Line

Probá estos comandos en la línea de abajo:

```
LINE 0,0 10,0
CIRCLE 5,5 3
RECTANG 0,0 10,5
TEXT 5,2 Hola Zipaquirá
LAYER NEW walls
LAYER SET walls
ZOOM E
SAVE
SCRIPT scripts/apto_66m2.scr
```

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 60 passed
```

---

## 🗂️ Project Structure

```
src/
├── model/          # Entidades, capas, snap engine, document (undo/redo)
├── view/           # Qt GUI, CadView (zoom/pan/Y-flip), GfxItems, UI
├── controller/     # 30 herramientas + command pattern (undo/redo)
├── io/             # .cadlite JSON, DXF export, SCRIPT engine (.scr)
└── main.py         # Entry point
tests/              # 60 pytest tests
scripts/            # Demo: generate_apto.py, apto_66m2.scr
```

---

## 🎨 Retro UI Color Palette

| Elemento | Color |
|----------|-------|
| Screen menu bg | `#0000AA` (VGA blue clásico) |
| Grid | `#0a1a2a` |
| Text | `#FFFFFF` |
| Headers | `#44AAFF` |
| Info bar | `#000088` |
| Accent | `#FFCC00` |

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
