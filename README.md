# DogCAD 2D Lite 🔥🐾

> *"Si AutoCAD R10 y Python tuvieran un hijo en Zipaquirá"*

```
   ▄████▄   ██████╗  ██████╗  ██████╗ █████╗ ██████╗
  ██▀  ▀██  ██╔══██╗██╔════╝ ██╔════╝██╔══██╗██╔══██╗
  ██    ██  ██║  ██║██║  ███╗██║     ██║  ██║██║  ██║
  ▀█▄  ▄█▀  ██║  ██║██║   ██║██║     ██║  ██║██║  ██║
   ▀████▀   ██████╔╝╚██████╔╝╚██████╗╚█████╔╝██████╔╝
            ╚═════╝  ╚═════╝  ╚═════╝ ╚════╝ ╚═════╝
           2D LITE  ·  FORK ACAD R10  ·  v1.0
```

**Desktop 2D CAD profesional. Hecho en Zipaquirá, Cundinamarca 🇨🇴. 99 tests. 8,953 líneas. 30+ herramientas. 0 dólares a Autodesk.**

---

## ⚡ Instalación

```bash
git clone https://github.com/gcorrea2005/cad2d-lite.git
cd cad2d-lite
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

---

## 📊 Stats

```
  99 tests ✅  |  101 archivos .py  |  8,953 líneas
  30+ tools    |  43 vars SETVAR    |  11 modos OSNAP
  15 linetypes |  ACI 256 colores   |  4 tipos de cota
  BLOQUES      |  PLOT PDF A4-A0   |  DXF IN/OUT
```

---

## 🔧 Todas las herramientas

| Menú | Comandos |
|------|----------|
| **DRAW** | LINE, ARC, CIRCLE, PLINE, RECTANG, TEXT, DIM, POINT, ELLIPSE, HATCH, SOLID, DONUT |
| **DIM** | LINEAR, ALIGNED, RADIUS, DIAMETER, ANGULAR, BASELINE |
| **MODIFY** | ERASE, MOVE, COPY, ROTATE, MIRROR, SCALE, OFFSET, TRIM, EXTEND, FILLET, CHAMFER, BREAK, EXPLODE, ARRAY, STRETCH |
| **DISPLAY** | ZOOM E, ZOOM W, ZOOM P, ZOOM IN, ZOOM OUT, PAN, REDRAW, REGEN |
| **INQUIRY** | DIST, AREA, ID, LIST, STATUS |
| **LAYER** | LAYER, CLAYER, ON, OFF, FREEZE, THAW, LOCK, UNLOCK, COLOR, LINETYPE, DELETE |
| **BLOQUES** | BLOCK, INSERT, DOOR, WINDOW |
| **SETTINGS** | COLOR, LINETYPE, SNAP, GRID, ORTHO, UNITS, LIMITS, SETVAR, TEMPLATE |
| **I/O** | SAVE, OPEN, PLOT (PDF), DXF IN, DXF OUT, SCRIPT |

---

## 🎯 OSNAP — 11 modos con prioridad

```
ENDPOINT > MIDPOINT > CENTER > NODE > QUADRANT > INTERSECTION
> INSERTION > PERPENDICULAR > TANGENT > NEAREST (+ QUICK)
```

---

## ⚙️ SETVAR — 43 variables de sistema

```
SETVAR OSMODE 7        → END+MID+CEN
SETVAR PDMODE 35       → X con círculo
SETVAR CECOLOR 1       → Rojo
SETVAR FILLETRAD 0.5   → Radio de empalme
SETVAR OFFSETDIST 2    → Distancia de offset
SETVAR DIMSCALE 1      → Escala de cotas
SETVAR ? DIM*          → Listar vars de dimensión
```

---

## 🎨 ACI 256 colores

Paleta completa AutoCAD Color Index. `COLOR 1` (rojo) a `COLOR 255` (blanco). BYLAYER y BYBLOCK.

---

## ⌨️ Atajos

```
L C A P R T D M O X S  → Tools (S=Stretch)
Esc                    → Cancelar → línea de comandos
Click Derecho          → Repetir último comando
F2                     → Text screen
F7 F8 F9               → Grid / Ortho / Snap
↑ ↓                    → Historial de comandos
Ctrl+Z / Ctrl+Y        → Undo / Redo
```

---

## 📟 Comandos rápidos

```
LINE 0,0 100,50        → Línea
CIRCLE 50,50 25        → Círculo
RECTANG 0,0 10,5       → Rectángulo
@100,0                 → Relativo cartesiano
@200<45                → Relativo polar
COLOR 1                → ACI red
LINETYPE CENTER        → Línea de eje
UNITS 5                → Metros
TEMPLATE               → 12 capas arquitectónicas
DOOR 0.9               → Puerta 90cm
HELP                   → Documentación en Safari
```

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 99 passed in 2.50s
```

---

## 🗂️ Estructura

```
src/
├── model/          # Entidades, capas, snap, ACI, SETVAR, linetypes, hatch
├── view/           # Qt GUI, CadView, CrosshairOverlay, GfxItems, pug icon
├── controller/     # 30+ tools, command pattern, undo/redo
├── io/             # .cadlite JSON, DXF in/out, SCRIPT engine
└── main.py
tests/              # 99 tests
docs/               # HTML doc (HELP command → Safari)
```

---

## 👨‍💻 Autor

**Ing. Giovanni Correa Mejía** — Zipaquirá, Cundinamarca 🇨🇴

Hecho con Python, PySide6, ezdxf, pan de sagú y puro vicio.
Dedicado a la memoria de AutoCAD R10 (1988) — DOS, EGA/VGA, diskettes de 5¼.

---

## 📜 Licencia

MIT — dibuje sin miedo, exporte sin culpa.
