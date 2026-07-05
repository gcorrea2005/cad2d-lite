# DogCAD 2D Lite 🔥🐾

> *"Si AutoCAD R10 y Python tuvieran un hijo en Zipaquirá"*

```
   ▄████▄   ██████╗  ██████╗  ██████╗ █████╗ ██████╗
  ██▀  ▀██  ██╔══██╗██╔════╝ ██╔════╝██╔══██╗██╔══██╗
  ██    ██  ██║  ██║██║  ███╗██║     ██║  ██║██║  ██║
  ▀█▄  ▄█▀  ██║  ██║██║   ██║██║     ██║  ██║██║  ██║
   ▀████▀   ██████╔╝╚██████╔╝╚██████╗╚█████╔╝██████╔╝
            ╚═════╝  ╚═════╝  ╚═════╝ ╚════╝ ╚═════╝
           FORK COMPLETO DE AUTOCAD R10 (1988) · v1.0
```

**Desktop 2D CAD profesional. Hecho en Zipaquirá, Cundinamarca 🇨🇴.**

```
99 tests ✅  |  101 archivos .py  |  8,953 líneas de código
30+ herramientas  |  43 vars SETVAR  |  11 modos OSNAP
15 tipos de línea  |  ACI 256 colores  |  6 tipos de cota
BLOQUES + INSERT  |  PLOT PDF A4-A0  |  DXF IN/OUT
```

---

## ⚡ Quick Start

```bash
git clone https://github.com/gcorrea2005/cad2d-lite.git
cd cad2d-lite
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

**Requisitos:** Python 3.12+, PySide6 6.11+, ezdxf 1.1+, pytest 9.1+

---

## 🏗️ Arquitectura MVC

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   MODEL     │     │    VIEW     │     │   CONTROLLER    │
│             │     │             │     │                 │
│ Document   │◄───▶│ MainWindow  │◄───▶│ ToolManager     │
│ CadEntity  │     │ CadView     │     │ BaseTool        │
│ LayerMgr   │     │ GfxItems    │     │ 30+ Tools       │
│ SnapEngine │     │ ScreenMenu  │     │ ModifyCmd       │
│ SysVars    │     │ Crosshair   │     │ Undo/Redo       │
│ ACI 256    │     │ StatusBar   │     │ ScriptEngine    │
│ Linetypes  │     │ PugIcon     │     │                 │
│ HatchDefs  │     │             │     │                 │
│ BlockDef   │     │             │     │                 │
└────────────┘     └────────────┘     └─────────────────┘
        │                  │                    │
        └──────────────────┼────────────────────┘
                           │
                    ┌──────┴──────┐
                    │     I/O     │
                    │ .cadlite    │
                    │ DXF in/out  │
                    │ PLOT PDF    │
                    │ SCRIPT .scr │
                    └─────────────┘
```

### Capa Modelo (`src/model/`)

- **`document.py`** — Documento central: diccionario de entidades (uuid → CadEntity), undo/redo stack (Command pattern), block_defs.
- **`entities/`** — 9 entidades geométricas: `Line`, `Circle`, `Arc`, `Polyline`, `TextEntity`, `Dimension`, `PointEntity`, `Ellipse`, `BlockInstance`. Cada una hereda de `CadEntity` (abstracto: `to_dict()`, `from_dict()`, `bounding_box()`).
- **`snap.py`** — SnapEngine con 11 modos OSNAP: ENDPOINT, MIDPOINT, CENTER, NODE, QUADRANT, INTERSECTION, INSERTION, PERPENDICULAR, TANGENT, NEAREST, QUICK. Prioridad por diccionario. Soporta intersección línea-línea, línea-círculo, círculo-círculo.
- **`sysvars.py`** — 43 variables de sistema en 7 bloques (A-G): OSMODE, PDMODE, PDSIZE, CECOLOR, CELTYPE, FILLETRAD, DIMSCALE, LTSCALE, SNAPUNIT... Validación por tipo. Wildcard `SETVAR ? DIM*`.
- **`aci.py`** — Mapeo completo ACI 256 → RGB con nombres. `parse_color("red")` → 1, `aci_to_rgb(1)` → (255,0,0).
- **`linetype_defs.py`** — 15 tipos de línea ACAD: CONTINUOUS, DASHED, HIDDEN, CENTER, PHANTOM, DASHDOT, BORDER, DIVIDE... Definidos como secuencias dash/gap/dot.
- **`hatch_patterns.py`** — 8 patrones: ANSI31 (ladrillo 45°), ANSI32 (acero cruzado), ANSI35 (concreto), SOLID... Render con QPainter + clip path.
- **`units.py`** — Formateo de distancias: Decimal, Engineering, Architectural (ft-in), Metric (m/cm/mm).

### Capa Vista (`src/view/`)

- **`cad_view.py`** — QGraphicsView con `scale(1, -1)` para Y+ arriba (estilo ACAD). CrosshairOverlay (QWidget transparente para cruceta). Zoom stack con `_save_viewport()` + `zoom_previous()`. Manejo de eventos: left=draw, right=repeat last, ESC=focus cmd line. F2/F7/F8/F9 keys.
- **`graphics/entity_items.py`** — GfxItems por entidad: `GfxLineItem`, `GfxCircleItem`, `GfxArcItem`, `GfxPolylineItem`, `GfxTextItem`, `GfxDimensionItem`, `GfxPointItem`, `GfxEllipseItem`. Cada uno implementa `paint()` con soporte ACI, linetype, PDMODE/PDSIZE. `_entity_color()` resuelve ACI + BYLAYER/BYBLOCK → QColor. `_entity_pen()` aplica dash pattern del linetype.
- **`ui/main_window.py`** — 2,000+ líneas. Screen menu ACAD10 (QListWidget, items A-Z). Command line con history (↑↓), caret verde. Status bar: LAYER/COLOR/LINETYPE/coords/file. Menú DIM con 6 tipos. 100+ command handlers. PLOT PDF via QPrinter. DXF IN via ezdxf con bulges.
- **`ui/pug_icon.py`** — Icono del pug dibujado con QPainter (orejas, ojos, nariz, lengua).

### Capa Controlador (`src/controller/`)

- **`tool_manager.py`** — Registry de tools. `activate_tool()` → deactivate anterior → activate nueva → setCursor.
- **`tools/`** — 36 tools. Cada una hereda de `BaseTool` (snap, layer, color, linetype, preview). Patrón: `mouse_press` + `mouse_move` + `mouse_release` + `deactivate`.
- **`commands/`** — Command pattern para undo/redo: `AddEntityCommand`, `DeleteEntityCommand`, `ModifyEntityCommand`.

### Capa I/O (`src/io/`)

- **`cad_file.py`** — Save/load `.cadlite` (JSON). `ENTITY_CLASSES` dict para deserialización polimórfica.
- **`dxf_export.py`** — Export a DXF R2010 vía ezdxf.
- **`dxf_import.py`** — Import DXF: LINE, CIRCLE, ARC, LWPOLYLINE (con bulges → arcos), TEXT, DIMENSION. Mapeo de layers y ACI colors.
- **`script_engine.py`** — Ejecución de comandos por lote (.scr). Soporta coordenadas relativas `@100,0` y polares `@200<45`. LASTPOINT tracking.

---

## 🔧 Todas las herramientas

| Menú | Comandos | Archivos |
|------|----------|----------|
| **DRAW** | ARC, CIRCLE, DIM, DONUT, ELLIPSE, HATCH, LINE, PLINE, POINT, RECTANG, SOLID, TEXT | 12 tools |
| **DIM** | ALIGNED, ANGULAR, BASELINE, DIAMETER, LINEAR, RADIUS | 3 tools + dim_radius |
| **MODIFY** | ARRAY, BREAK, CHAMFER, COPY, ERASE, EXPLODE, EXTEND, FILLET, MIRROR, MOVE, OFFSET, ROTATE, SCALE, STRETCH, TRIM | 15 tools |
| **DISPLAY** | PAN, REDRAW, REGEN, ZOOM E, ZOOM IN, ZOOM OUT, ZOOM P, ZOOM W | 2 tools + cad_view |
| **INQUIRY** | AREA, DIST, ID, LIST, STATUS | 3 tools |
| **LAYER** | COLOR, DELETE, FREEZE, LINETYPE, LOCK, MAKE, NEW, OFF, ON, SET, THAW, UNLOCK, ? | main_window handlers |
| **BLOQUES** | BLOCK, INSERT, DOOR, WINDOW | block.py + library |
| **SETTINGS** | COLOR, GRID, LIMITS, LINETYPE, ORTHO, SETVAR, SNAP, UNITS | sysvars.py |
| **I/O** | DXF IN, DXF OUT, OPEN, PLOT, SAVE, SCRIPT | io/ module |

---

## 🎯 OSNAP — 11 modos con prioridad

```
Prioridad 0: ENDPOINT    → Extremos de Line/Arc/Pline
Prioridad 1: MIDPOINT    → Punto medio
Prioridad 2: CENTER      → Centro de Circle/Arc
Prioridad 3: NODE        → Point entity
Prioridad 4: QUADRANT    → 0/90/180/270° de Circle/Arc
Prioridad 5: INTERSECTION → Cruce Line-Line, Line-Circle, Circle-Circle
Prioridad 6: INSERTION   → Punto de inserción de Text
Prioridad 7: PERPENDICULAR → Pie de perpendicular
Prioridad 8: TANGENT     → Tangente a Circle/Arc
Prioridad 9: NEAREST     → Punto más cercano
           QUICK         → Acepta primer snap (sin ordenar por prioridad)
```

OSMODE bitmask: `SETVAR OSMODE 7` = END(1) + MID(2) + CEN(4)

---

## ⚙️ SETVAR — 43 variables

| Bloque | Count | Variables |
|--------|-------|-----------|
| A — Imprescindibles | 12 | OSMODE, APERTURE, PICKBOX, ORTHOMODE, COORDS, CLAYER, FILLETRAD, CHAMFERA, CHAMFERB, TEXTSIZE, OFFSETDIST, MIRRTEXT |
| B — Dimensionado | 8 | DIMSCALE, DIMTXT, DIMASZ, DIMEXO, DIMEXE, DIMDLI, DIMTAD, DIMZIN |
| C — Grid/Snap | 6 | GRIDMODE, GRIDUNIT, SNAPMODE, SNAPUNIT, LIMMIN, LIMMAX |
| D — Estilo | 4 | CECOLOR, CELTYPE, LTSCALE, FILLMODE |
| E — Unidades | 3 | LUNITS, LUPREC, AUNITS |
| F — Estado | 4 | BLIPMODE, EXPERT, DRAGMODE, CMDECHO |
| G — Read-only | 6 | LASTPOINT, LASTANGLE, DWGNAME, ACADVER(R10), PDMODE, PDSIZE |

---

## 🎨 ACI 256 Color Palette

```python
from src.model.aci import aci_to_rgb, parse_color, COLOR_NAMES

aci_to_rgb(1)    # → (255, 0, 0)    Red
aci_to_rgb(7)    # → (255, 255, 255) White (default)
parse_color("red") # → 1
parse_color("bylayer") # → "BYLAYER"
```

Mapeo HSV-based para índices 1-255. Nombres: Red, Yellow, Green, Cyan, Blue, Magenta, White.

---

## 📏 LINETYPES — 15 tipos

| Linetype | Descripción |
|----------|-------------|
| CONTINUOUS | Línea sólida (default) |
| DASHED | - - - - (12.7, -6.35) |
| HIDDEN | _ _ _ _ (6.35, -3.175) |
| CENTER | -- - -- - (31.75, -6.35, 6.35, -6.35) |
| PHANTOM | -- - - -- (31.75, -6.35, 6.35, -6.35, 6.35, -6.35) |
| DASHDOT | - . - . (12.7, -6.35, 0, -6.35) |
| BORDER, DIVIDE, DOT, DOT2, DOTX2, HIDDEN2, HIDDENX2, CENTER2, CENTERX2 | Variantes |

---

## 📊 DIMENSION — 6 tipos

| Tipo | Render | Comando |
|------|--------|---------|
| LINEAR | Ext lines + dim line + arrows + text | DIM |
| ALIGNED | Rotado al ángulo de los puntos | DIMALIGNED |
| RADIUS | Leader + arrow + "R 5.00" | DIMRADIUS |
| DIAMETER | Leader + arrow + "⌀ 10.00" | DIMDIAMETER |
| ANGULAR | Rays + arc + "45.0°" | DIMANGULAR |
| BASELINE | Cadena desde origen, offset stacking | DIMBASELINE |

Arrowheads: triángulos rellenos de 6px (DIMASZ). Texto centrado con fontMetrics. Extension lines con offset (DIMEXO). Texto rotado para aligned y vertical.

---

## 🧱 HATCH — 8 patrones

| Patrón | Descripción | Ángulo |
|--------|-------------|--------|
| ANSI31 | Ladrillo / mampostería | 45° |
| ANSI32 | Acero (cross-hatch) | 45° + 135° |
| ANSI33 | Bronce / latón | 45° + 135° + 0° + 90° |
| ANSI34 | Plástico / caucho | 45° + 135° + 0° |
| ANSI35 | Concreto (sand + gravel) | 45° + 135° staggered |
| ANSI36 | Tierra | 0° + 90° + 45° + 135° |
| ANSI37 | Plomo / zinc | 45° + 135° |
| ANSI38 | Aluminio | 45° + 135° + 0° |
| SOLID | Relleno sólido | — |

Detección de boundary: ray-casting point-in-polygon. Clip al polígono con QPainterPath.

---

## 📦 BLOQUES

```python
# Block definition (grupo de entidades con nombre + punto base)
class BlockDefinition:
    name: str
    entities: list[CadEntity]
    base_point: Point

# Block instance (referencia insertada en el dibujo)
class BlockInstance(CadEntity):
    block_name: str
    insertion_point: Point
    scale_x: float
    scale_y: float
    rotation: float  # degrees
```

Transformación: translate(-base) → scale(sx, sy) → rotate(θ) → translate(+insertion).

Librería built-in: `DOOR 0.9` (arco + panel 90cm), `WINDOW 1.2` (frame + mullion 120cm).

---

## 🖨️ PLOT — PDF con escala

```python
# QPrinter → QPainter → scene.render()
# Paper: A4, A3, A2, A1, A0
# Scales: 1:1, 1:2, 1:5, 1:10, 1:20, 1:50, 1:100, 1:200, 1:500, Fit
```

El PDF se abre automáticamente después de generarse.

---

## 📟 Comandos

```
LINE 0,0 100,50          # Línea absoluta
@100,0                   # Relativo cartesiano desde LASTPOINT
@200<45                  # Relativo polar desde LASTPOINT
CIRCLE 50,50 25          # Círculo centro+radio
RECTANG 0,0 10,5         # Rectángulo 2 esquinas
COLOR 1                  # Set color (1=Red, BYLAYER, BYBLOCK)
LINETYPE CENTER          # Set tipo de línea
CLAYER walls             # Cambiar capa actual
LAYER                    # Listar capas
UNITS 5                  # Cambiar a metros (5=m, 6=cm, 7=mm, 2=decimal)
TEMPLATE                 # 12 capas arquitectónicas
SETVAR OSMODE 7          # END+MID+CEN
SETVAR PDMODE 35         # Punto: X con círculo
SETVAR ? DIM*            # Listar vars de dimensión
DOOR 0.9                 # Puerta 90cm en LASTPOINT
WINDOW 1.2               # Ventana 120cm en LASTPOINT
CHPROP COLOR 1           # Cambiar color de entidad seleccionada
CHPROP LINETYPE DASHED   # Cambiar linetype de entidad seleccionada
DIMALIGNED               # Cota alineada
DIMBASELINE              # Cadena de cotas
DXFIN                    # Importar DXF
PLOT                     # Exportar PDF
ZOOM E / ZOOM W / ZOOM P / ZOOM IN / ZOOM OUT
PAN / REDRAW / REGEN
DIST / AREA / ID / LIST / STATUS
HELP                     # Abrir docs en Safari
ABOUT                    # Diálogo psicodélico
```

---

## ⌨️ Atajos

| Tecla | Acción |
|-------|--------|
| `L C A P R T D M O X S` | Tools (S=Stretch) |
| `Esc` | Cancelar → foco línea comandos (cursor verde blink) |
| `Click Der` | Repetir último comando |
| `F2` | Text screen toggle |
| `F7` | Grid toggle |
| `F8` | Ortho toggle |
| `F9` | Snap toggle |
| `↑ ↓` | Historial de comandos (preserva draft) |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 99 passed in 2.50s
```

| Archivo | Qué prueba |
|---------|------------|
| `test_entities/` | Line, Circle, Arc, Polyline, Text, Dimension, Point, Ellipse |
| `test_entities/test_snap.py` | 11 modos OSNAP |
| `test_entities/test_snap_priority.py` | Prioridad de snaps |
| `test_aci_sysvars.py` | ACI palette + SETVAR engine |
| `test_layer.py` | Layer manager |
| `test_undo.py` | Undo/redo stack |
| `test_cad_file.py` | Save/load roundtrip |
| `test_commands.py` | Command processing |

---

## 🗂️ Estructura completa

```
cad2d-lite/
├── src/
│   ├── main.py                          # Entry point
│   ├── app.py                           # QApplication + MainWindow
│   ├── model/
│   │   ├── document.py                  # Documento central
│   │   ├── layer.py                     # Capa (name, color, linetype, visible, locked)
│   │   ├── layer_manager.py             # Gestor de capas
│   │   ├── snap.py                      # SnapEngine + 11 SnapTypes
│   │   ├── sysvars.py                   # 43 variables SETVAR
│   │   ├── aci.py                       # ACI 256 → RGB
│   │   ├── linetype_defs.py             # 15 tipos de línea
│   │   ├── hatch_patterns.py            # 8 patrones de sombreado
│   │   ├── units.py                     # Formateo de unidades
│   │   └── entities/
│   │       ├── base.py                  # CadEntity abstracto + Point
│   │       ├── line.py, circle.py, arc.py
│   │       ├── polyline.py, text.py
│   │       ├── dimension.py, point_entity.py
│   │       ├── ellipse.py, block.py
│   │       └── __init__.py
│   ├── view/
│   │   ├── cad_view.py                  # QGraphicsView (Y-up, crosshair, keys)
│   │   ├── cad_scene.py                 # QGraphicsScene
│   │   ├── graphics/
│   │   │   ├── entity_items.py          # GfxItems (paint, ACI, linetype, PDMODE)
│   │   │   └── grid_item.py             # Grid visual
│   │   └── ui/
│   │       ├── main_window.py           # 💀 2,000+ líneas
│   │       ├── psychedelic_about.py     # Diálogo ABOUT
│   │       └── pug_icon.py              # Icono pug QPainter
│   ├── controller/
│   │   ├── tool_manager.py              # Registry + switching
│   │   ├── tools/
│   │   │   ├── base_tool.py             # Snap, layer, color, linetype, preview
│   │   │   ├── select_tool.py           # Selección + GRIPS + stretch
│   │   │   ├── line_tool.py, circle_tool.py, arc_tool.py
│   │   │   ├── polyline_tool.py, rectangle_tool.py, text_tool.py
│   │   │   ├── dim_linear_tool.py, dim_radius_tool.py, dim_baseline_tool.py
│   │   │   ├── point_tool.py, solid_tool.py, hatch_tool.py
│   │   │   ├── ellipse_tool.py, donut_tool.py
│   │   │   ├── move_tool.py, copy_tool.py, rotate_tool.py
│   │   │   ├── mirror_tool.py, scale_tool.py, offset_tool.py
│   │   │   ├── trim_tool.py, extend_tool.py, fillet_tool.py
│   │   │   ├── chamfer_tool.py, break_tool.py, explode_tool.py
│   │   │   ├── array_tool.py, stretch_tool.py
│   │   │   ├── dist_tool.py, area_tool.py, id_tool.py
│   │   │   ├── zoom_win_tool.py, pan_tool.py
│   │   │   └── delete_tool.py
│   │   └── commands/
│   │       ├── base_command.py
│   │       ├── add_entity.py, delete_entity.py, modify_entity.py
│   │       └── __init__.py
│   └── io/
│       ├── cad_file.py                  # .cadlite JSON save/load
│       ├── dxf_export.py                # DXF R2010 export
│       ├── dxf_import.py                # DXF import (bulges, layers, colors)
│       └── script_engine.py             # .scr batch + coords @relativas
├── tests/
│   ├── test_entities/                   # 9 entity tests
│   ├── test_aci_sysvars.py              # ACI + SETVAR
│   ├── test_layer.py, test_undo.py
│   ├── test_cad_file.py, test_commands.py
│   └── conftest.py
├── docs/
│   └── index.html                       # Documentación HTML (HELP → Safari)
├── scripts/                             # Scripts de generación
├── .hermes/plans/                       # Planes de desarrollo
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🎨 UI

- **Fondo**: Negro puro `#000000` (drawing area)
- **Screen menu**: Azul VGA `#0000AA` (ACAD 10)
- **Grid**: `#0a1a2a` (dark blue)
- **Text**: `#FFFFFF` (white)
- **Headers**: `#44AAFF` (cyan)
- **Accent**: `#FFCC00` (yellow)
- **Status bar**: `#000088` (dark blue)
- **Crosshair**: Blanco alpha 180, pickbox verde `#00FF00`
- **Command cursor**: Verde `#00FF00`, 3px width, blink
- **Tipografía**: Courier New (monospace)

---

## 👨‍💻 Autor

**Ing. Giovanni Correa Mejía** — Zipaquirá, Cundinamarca 🇨🇴

Hecho con Python 3.12, PySide6 6.11, ezdxf 1.1, pytest 9.1, pan de sagú y puro vicio ingenieril.

Dedicado a la memoria de AutoCAD R10 (1988) — DOS 3.3, EGA/VGA 640x480, diskettes de 5¼, y el inconfundible screen menu azul.

---

## 📜 Licencia

MIT — dibuje sin miedo, exporte sin culpa, fork sin permiso.
