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
163 tests ✅  |  35 herramientas  |  11,450 líneas de código
DogLISP 🦎    |  CALC 🔢         |  Grips 🔲
Transient OSNAP 🎯 | DWG import 📦 | BLOQUES 🧱
43 vars SETVAR | 11 modos OSNAP  | 15 tipos de línea
ACI 256 colores | DXF IN/OUT     | PLOT PDF A4-A0
```

---

## ⚡ Quick Start

```bash
git clone https://github.com/gcorrea2005/cad2d-lite.git
cd cad2d-lite
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

**Requisitos:** Python 3.12+, PySide6 6.11+, ezdxf 1.1+, pytest 9.1+

**DWG Import (opcional):**
```bash
brew install libredwg    # macOS — archivos R12-R2013 simples
apt install libredwg     # Linux
```

**DWG complejos (R2010+):** usar [ODA FileConverter](https://www.opendesign.com/guestfiles/oda_file_converter) (gratuito) para convertir DWG→DXF, luego `DXFIN` en DogCAD.

---

## 🏗️ Arquitectura MVC

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   MODEL     │     │    VIEW     │     │   CONTROLLER     │
│             │     │             │     │                  │
│ Document   │◄───▶│ MainWindow  │◄───▶│ ToolManager      │
│ CadEntity  │     │ CadView     │     │ BaseTool         │
│ LayerMgr   │     │ GfxItems    │     │ 35+ Tools        │
│ SnapEngine │     │ ScreenMenu  │     │ Command History  │
│ SysVars    │     │ Crosshair   │     │ CalcEngine       │
│ ACI 256    │     │ StatusBar   │     │ Undo/Redo Stack  │
│ Linetypes  │     │ PugIcon     │     │ ScriptEngine     │
│ HatchDefs  │     │             │     │                  │
│ BlockDef   │     │             │     │                  │
└────────────┘     └─────────────┘     └──────────────────┘
       │                  │                    │
       └──────────────────┼────────────────────┘
                          │
                   ┌──────┴──────┐     ┌──────────────┐
                   │     I/O     │     │  SCRIPTING   │
                   │ .cadlite    │     │ DogLISP 🦎   │
                   │ DXF in/out  │     │ reader/eval  │
                   │ DWG in 📦   │     │ builtins     │
                   │ PLOT PDF    │     │ REPL         │
                   │ SCRIPT .scr │     │              │
                   └─────────────┘     └──────────────┘
```

### Capa Modelo (`src/model/`)

- **`document.py`** — Documento central: entidades (uuid → CadEntity), undo/redo stack (Command pattern), block_defs, autosave.
- **`entities/`** — 9 entidades: `Line`, `Circle`, `Arc`, `Polyline`, `TextEntity`, `Dimension`, `PointEntity`, `Ellipse`, `BlockInstance`. Heredan de `CadEntity` (abstracto: `to_dict()`, `from_dict()`, `bounding_box()`).
- **`snap.py`** — SnapEngine con 11 modos OSNAP: ENDPOINT, MIDPOINT, CENTER, NODE, QUADRANT, INTERSECTION, INSERTION, PERPENDICULAR, TANGENT, NEAREST, QUICK. Con prioridad. Intersección línea-línea, línea-círculo, círculo-círculo.
- **`sysvars.py`** — 43 variables de sistema en 7 bloques (A-G): OSMODE, PDMODE, PDSIZE, CECOLOR, CELTYPE, FILLETRAD, DIMSCALE, LTSCALE... Validación por tipo. Wildcard `SETVAR ? DIM*`.
- **`aci.py`** — ACI 256 → RGB con nombres. `parse_color("red")` → 1, `aci_to_rgb(1)` → (255,0,0).
- **`linetype_defs.py`** — 15 tipos: CONTINUOUS, DASHED, HIDDEN, CENTER, PHANTOM, DASHDOT, BORDER, DIVIDE... Dash/gap/dot sequences.
- **`hatch_patterns.py`** — 8 patrones: ANSI31 (ladrillo 45°), ANSI32 (acero), ANSI35 (concreto), SOLID... QPainter + clip path.
- **`units.py`** — Decimal, Engineering, Architectural (ft-in), Metric (m/cm/mm).

### Capa Vista (`src/view/`)

- **`cad_view.py`** — QGraphicsView `scale(1, -1)` para Y+ arriba. CrosshairOverlay. Zoom stack. Keys F2/F7/F8/F9. Left=draw, right=repeat, ESC=cmd line.
- **`graphics/entity_items.py`** — GfxItems: `GfxLineItem`, `GfxCircleItem`, `GfxArcItem`, `GfxPolylineItem`, `GfxTextItem`, `GfxDimensionItem`, `GfxPointItem`, `GfxEllipseItem`. ACI, linetype, PDMODE/PDSIZE.
- **`ui/main_window.py`** — Screen menu ACAD10 azul #0000AA, command line con caret verde, status bar, menú DIM, 100+ command handlers, PLOT PDF via QPrinter, DXF IN/OUT.
- **`ui/pug_icon.py`** — Icono pug QPainter.

### Capa Controlador (`src/controller/`)

- **`tool_manager.py`** — Registry de 35 tools. `activate_tool()` → deactivate → activate → setCursor.
- **`tools/`** — 35 tools heredando de `BaseTool`. Snap, layer, color, linetype, preview. Transient OSNAP override.
- **`calc_engine.py`** — CALC: calculadora geométrica con snaps interactivos. Recursive descent parser. Funciones trigonométricas, vectores, DIST, ANG.
- **`commands/`** — Command pattern: `AddEntityCommand`, `DeleteEntityCommand`, `ModifyEntityCommand`.

### Capa Scripting (`src/scripting/`)

- **`reader.py`** — Tokenizer + parser. Texto → AST S-expressions.
- **`eval.py`** — Interpreter core: Env, Lambda, Builtin. `eval_expr()` con soporte `defun`, `let`, `if`, `progn`.
- **`builtins.py`** — CAD builtins: `line`, `circle`, `arc`, `pline`, `rectang`, `text`, `point`, `hatch`, `solid`, `donut`, `ellipse`, `erase`, `move`, `copy`, `rotate`, `mirror`, `scale`, `offset`, `layer`, `ssget`, `osmode`, `cal`, `ver`, `setvar`, `zoom`, `limits`, `save`.
- **`repl.py`** — Read-Eval-Print Loop. `eval_text()`, `load_file()`.

### Capa I/O (`src/io/`)

- **`cad_file.py`** — Save/load `.cadlite` (JSON). `ENTITY_CLASSES` dict para deserialización polimórfica.
- **`dxf_export.py`** / **`dxf_import.py`** — DXF R2010 via ezdxf (LWPOLYLINE con bulges, capas, colores).
- **`dwg_io.py`** — DWG import via LibreDWG bridge. `dwg_to_dxf()` → DXF temporal → `import_dxf()`.
- **`minimal_dxf.py`** — Exportador DXF minimalista (solo ENTITIES) para DWG bridge.
- **`script_engine.py`** — `.scr` batch runner. Coordenadas @relativas y @polares.

---

## 🔧 Todas las Herramientas

| Menú | Comandos | Archivos |
|------|----------|----------|
| **DRAW** | ARC, CIRCLE, DIM, DONUT, ELLIPSE, HATCH, LINE, PLINE, POINT, RECTANG, SOLID, TEXT | 12 tools |
| **DIM** | ALIGNED, ANGULAR, BASELINE, DIAMETER, LINEAR, RADIUS | 3 tools |
| **MODIFY** | ARRAY, BREAK, CHAMFER, COPY, ERASE, EXPLODE, EXTEND, FILLET, MIRROR, MOVE, OFFSET, ROTATE, SCALE, STRETCH, TRIM, CHPROP | 16 tools |
| **DISPLAY** | PAN, REDRAW, REGEN, ZOOM E, ZOOM IN, ZOOM OUT, ZOOM P, ZOOM W | 2 tools |
| **INQUIRY** | AREA, DIST, ID, LIST, STATUS | 3 tools |
| **LAYER** | COLOR, DELETE, FREEZE, LINETYPE, LOCK, MAKE, NEW, OFF, ON, SET, THAW, UNLOCK, ? | handlers |
| **BLOQUES** | BLOCK, INSERT, DOOR, WINDOW | block.py |
| **SETTINGS** | COLOR, GRID, LIMITS, LINETYPE, ORTHO, SETVAR, SNAP, UNITS | sysvars.py |
| **I/O** | DXF IN, DXF OUT, DWG IN, OPEN, PLOT, SAVE, SCRIPT | io/ module |

---

## 🦎 DogLISP — Intérprete Lisp/Scheme

DogCAD tiene un intérprete Lisp/Scheme embebido. Cualquier texto que empiece con `(` en la command line se ejecuta como Lisp.

### Primeros pasos

```lisp
;; Dibujar geometría
(line (p 0 0) (p 1000 500))
(circle (p 500 500) 200)
(arc (p 0 0) 30 0 180)
(rectang (p 0 0) (p 100 50))
(pline (list (p 0 0) (p 50 100) (p 100 0)))

;; Capas y snaps
(layer "set" "MUROS")
(osmode "END,MID,INT")
(cal "100*2")           ;; → 200

;; Guardar y zoom
(save)
(zoom "E")
```

### Definir funciones

```lisp
(defun cuadrado (x y lado)
  (rectang (p x y) (p (+ x lado) (+ y lado))))

(cuadrado 100 100 50)

;; Grilla de columnas
(defun grilla (x y cols filas sep)
  (if (> filas 0)
      (progn
        (grilla-fila x y cols sep)
        (grilla x (+ y sep) cols (- filas 1) sep))))

(defun grilla-fila (x y n sep)
  (if (> n 0)
      (progn
        (rectang (p x y) (p (+ x 30) (+ y 30)))
        (grilla-fila (+ x sep) y (- n 1) sep))))

(grilla 0 0 5 4 500)
```

### Comandos

| Comando | Acción |
|---------|--------|
| `(expr)` | Evalúa expresión Lisp directamente |
| `LISP expr` | Evalúa expresión |
| `LSPLOAD file.lsp` | Carga archivo .lsp |
| `APPLOAD` | Diálogo para cargar .lsp |

### Builtins CAD

| Categoría | Funciones |
|-----------|-----------|
| Dibujo | `line`, `circle`, `arc`, `pline`, `rectang`, `text`, `point`, `solid`, `hatch`, `donut`, `ellipse` |
| Modificar | `erase`, `move`, `copy`, `rotate`, `mirror`, `scale`, `offset` |
| Capas | `layer` (set/new/on/off/color/freeze/thaw/lock/unlock) |
| Selección | `ssget` (ALL, layer, window) |
| Sistema | `osmode`, `cal`, `ver`, `setvar`, `zoom`, `limits`, `save` |
| Utilidades | `p`, `list`, `defun`, `let`, `if`, `progn`, `lambda` |

---

## 🔢 CALC — Calculadora Geométrica

Evalúa expresiones matemáticas con snaps interactivos. Combiná puntos geométricos con aritmética.

```lisp
;; Punto medio entre dos extremos
CAL (END+END)/2          → click en 2 puntos

;; Matemática pura
CAL 100*2                → 200
CAL SQRT(144)            → 12
CAL SIN(45)              → 0.707106...

;; Offset de un punto
CAL END+[100,0]          → 100mm a la derecha del endpoint

;; Distancia y ángulo
CAL DIST(END,END)        → distancia entre dos clicks
CAL ANG(END,END)         → ángulo en grados
```

**Snaps:** END, MID, CEN, INT, PER, NEA, QUA, TAN, NOD, INS
**Funciones:** SIN, COS, TAN, ASIN, ACOS, ATAN, ATAN2, SQRT, EXP, LN, LOG, POW, ABS, ROUND, FLOOR, CEIL, MIN, MAX, D2R, R2D, PI
**Vectores:** DIST(p1,p2), VEC(p1,p2), ANG(p1,p2), [x,y] literals

---

## 🎯 OSNAP — 11 modos con precisión

### Transient OSNAP Override 🔥

Durante cualquier herramienta activa (LINE, CIRCLE, MOVE...), escribí el nombre del snap y se fuerza SOLO para el siguiente pick. No cambia el OSMODE global.

```
LINE        → activa herramienta
END         → fuerza snap ENDPOINT (solo este pick)
[click]     → snap al extremo
PER         → fuerza PERPENDICULAR (solo este pick)
[click]     → perpendicular desde el primer punto
```

Snaps disponibles: `END`, `MID`, `CEN`, `NOD`, `QUA`, `INT`, `INS`, `PER`, `TAN`, `NEA`

### OSMODE Bitmask

```
Prioridad 0: ENDPOINT    → Extremos (bit 1)
Prioridad 1: MIDPOINT    → Punto medio (bit 2)
Prioridad 2: CENTER      → Centro Circle/Arc (bit 4)
Prioridad 3: NODE        → Point entity (bit 8)
Prioridad 4: QUADRANT    → 0/90/180/270° (bit 16)
Prioridad 5: INTERSECTION → Cruce Line/Line/Circle (bit 32)
Prioridad 6: INSERTION   → Text (bit 64)
Prioridad 7: PERPENDICULAR → Pie perpendicular (bit 128)
Prioridad 8: TANGENT     → Tangente (bit 256)
Prioridad 9: NEAREST     → Más cercano (bit 512)
           QUICK         → Primer snap sin ordenar
```

```bash
OSNAP END,MID,INT        # combinación mágica (cubre 90% de casos)
OSNAP 7                  # END(1) + MID(2) + CEN(4)
F9                       # toggle snap rápido
```

### Snap Glyphs (AutoCAD-style indicators)

| SnapType | Glyph |
|---|---|
| ENDPOINT | □ Cuadrado verde |
| MIDPOINT | △ Triángulo |
| CENTER | ○+ Círculo con cruz |
| QUADRANT | ◇ Diamante |
| INTERSECTION | ✕ X |
| PERPENDICULAR | ∟ Ángulo recto |
| TANGENT | ○— Círculo con tangente |
| NEAREST | ⧖ Reloj de arena |

---

## 🔲 GRIPS — Edición Directa

Al seleccionar una entidad, cuadrados azules en sus puntos clave. Hover → imán naranja (12px). Arrastrar para editar.

**Modos (Space/Enter cicla):**
- **Stretch** — mueve el grip deformando la entidad
- **Move** — traslada la entidad completa
- **Rotate** — rota alrededor del grip opuesto
- **Scale** — escala desde el grip opuesto

**Grip points por entidad:** Line (3), Circle (5), Arc (4), Polyline (vértices + midpoints), Ellipse (5), Point (1), Text (1)

---

## 📦 DWG Import

DogCAD importa archivos DWG via LibreDWG bridge (archivos simples R12-R2013).

```bash
# Instalar LibreDWG
brew install libredwg

# En DogCAD:
DXFIN          # comando unificado → acepta .dxf y .dwg
DWGFIN         # alias específico para DWG
# o FILE → DXF/DWG IN
```

**Soporte:** DWG R12-R2013 para archivos simples. Para DWG complejos (R2010+ con previews grandes, bloques anidados, objetos proxy), usar [ODA FileConverter](https://www.opendesign.com/guestfiles/oda_file_converter) (gratuito):

```bash
ODAFileConverter drawing.dwg drawing.dxf ACAD2018 DXF 0 1
# Luego en DogCAD: DXFIN → drawing.dxf
```

ODA es el estándar industrial — lo usan QCAD, BricsCAD, y todos los CAD no-Autodesk.

---

## 📜 SCRIPT .scr — Automatización por Lotes

Ejecutá archivos .scr con comandos AutoCAD clásicos. Soporta coordenadas relativas y polares.

```bash
# Coordenadas absolutas
LINE 0,0 1000,0

# Relativas (@dx,dy desde LASTPOINT)
LINE 0,0 @1000,0
@0,800

# Polares (@distancia<ángulo)
LINE 0,0 @200<45
@200<120
```

**Comandos soportados:** LINE, CIRCLE, ARC, RECTANG, PLINE, TEXT, POINT, DIM, LAYER NEW/SET/ON/OFF/COLOR, ZOOM E/W, LIMITS, SAVE, SAVEAS, ERASE ALL/LAYER, UNDO, REDO, DELAY ms, ; comentarios

### Generador Python para cerchas

```bash
python templates/truss-generator.py --out cercha.scr \
    --widths 900,900,900,825,900,900,900,470 \
    --diag up --invert-at 4 --height 1000
```

---

## 🎯 OSNAP — 11 modos con prioridad

Opciones para configuración manual:

```
OSNAP END,MID,INT        # combinación más útil (90% de los casos)
OSNAP 7                  # END(1) + MID(2) + CEN(4) por bitmask
OSNAP OFF                # desactivar
SETVAR OSMODE 35         # END+MID+INT (1+2+32)
F9                       # toggle snap rápido
```

---

## ⚙️ SETVAR — 43 variables de sistema

| Bloque | Count | Variables |
|--------|-------|-----------|
| A — Imprescindibles | 12 | OSMODE, APERTURE, PICKBOX, ORTHOMODE, COORDS, CLAYER, FILLETRAD, CHAMFERA, CHAMFERB, TEXTSIZE, OFFSETDIST, MIRRTEXT |
| B — Dimensionado | 8 | DIMSCALE, DIMTXT, DIMASZ, DIMEXO, DIMEXE, DIMDLI, DIMTAD, DIMZIN |
| C — Grid/Snap | 6 | GRIDMODE, GRIDUNIT, SNAPMODE, SNAPUNIT, LIMMIN, LIMMAX |
| D — Estilo | 4 | CECOLOR, CELTYPE, LTSCALE, FILLMODE |
| E — Unidades | 3 | LUNITS, LUPREC, AUNITS |
| F — Estado | 4 | BLIPMODE, EXPERT, DRAGMODE, CMDECHO |
| G — Read-only | 6 | LASTPOINT, LASTANGLE, DWGNAME, ACADVER(R10), PDMODE, PDSIZE |

```bash
SETVAR OSMODE 7          # leer/escribir
SETVAR ? DIM*            # wildcard: lista vars de dimensión
SETVAR                   # lista todas
```

---

## 🎨 ACI 256 Color Palette

```python
from src.model.aci import aci_to_rgb, parse_color

aci_to_rgb(1)     # → (255, 0, 0)    Red
aci_to_rgb(7)     # → (255, 255, 255) White (default)
parse_color("red") # → 1
parse_color("bylayer") # → "BYLAYER"
```

---

## 📏 LINETYPES — 15 tipos

| Linetype | Patrón |
|----------|--------|
| CONTINUOUS | _________ (default) |
| DASHED | - - - - (12.7, -6.35) |
| HIDDEN | _ _ _ _ (6.35, -3.175) |
| CENTER | -- - -- - (31.75, -6.35, 6.35, -6.35) |
| PHANTOM | -- - - -- |
| DASHDOT | - . - . |
| BORDER, DIVIDE, DOT, DOT2, DOTX2, HIDDEN2, HIDDENX2, CENTER2, CENTERX2 | Variantes |

---

## 📊 DIMENSION — 6 tipos

| Tipo | Render | Comando |
|------|--------|---------|
| LINEAR | Ext lines + dim line + arrows + text | DIM |
| ALIGNED | Rotado al ángulo | DIMALIGNED |
| RADIUS | Leader + "R 5.00" | DIMRADIUS |
| DIAMETER | Leader + "⌀ 10.00" | DIMDIAMETER |
| ANGULAR | Rays + arc + "45.0°" | DIMANGULAR |
| BASELINE | Cadena desde origen | DIMBASELINE |

**Variables DIM:** DIMSCALE, DIMTXT, DIMASZ, DIMEXO, DIMEXE, DIMDLI, DIMTAD, DIMZIN

---

## 🧱 HATCH — 8 patrones

| Patrón | Uso | Ángulo |
|--------|-----|--------|
| ANSI31 | Ladrillo / mampostería | 45° |
| ANSI32 | Acero (cross-hatch) | 45° + 135° |
| ANSI35 | Concreto | 45° + 135° staggered |
| SOLID | Relleno sólido | — |

Detección de boundary: ray-casting point-in-polygon. Clip con QPainterPath.

---

## 📦 BLOQUES

```python
class BlockDefinition:
    name: str
    entities: list[CadEntity]
    base_point: Point

class BlockInstance(CadEntity):
    block_name: str
    insertion_point: Point
    scale_x, scale_y: float
    rotation: float  # degrees
```

Librería built-in: `DOOR 0.9` (puerta 90cm), `WINDOW 1.2` (ventana 120cm).

---

## 🖨️ PLOT — PDF con escala

```python
# QPrinter → QPainter → scene.render()
# Paper: A4, A3, A2, A1, A0
# Scales: 1:1, 1:10, 1:20, 1:50, 1:100, 1:200, 1:500, Fit
```

El PDF se abre automáticamente al generarse.

---

## 📟 Comandos — Referencia Rápida

```
LINE 0,0 100,50           # Línea absoluta
@100,0                    # Relativo cartesiano
@200<45                   # Relativo polar
CIRCLE 50,50 25           # Círculo centro+radio
RECTANG 0,0 10,5          # Rectángulo
COLOR 1                   # ACI color
LINETYPE CENTER           # Tipo de línea
CLAYER walls              # Cambiar capa
LAYER ?                   # Listar capas
TEMPLATE                  # 12 capas arquitectónicas
SETVAR OSMODE 7           # END+MID+CEN
SETVAR PDMODE 35          # Punto estilo X+circle
SETVAR ? DIM*             # Wildcard
DOOR 0.9                  # Puerta 90cm
WINDOW 1.2                # Ventana 120cm
CHPROP COLOR 1            # Cambiar color selección
DIMALIGNED                # Cota alineada
DIMBASELINE               # Cadena cotas
DXFIN / DWGFIN            # Importar DXF/DWG
PLOT                      # PDF
ZOOM E / ZOOM W / ZOOM P / ZOOM IN / ZOOM OUT
PAN / REDRAW / REGEN
DIST / AREA / ID / LIST / STATUS
UNITS 5                   # metros
PURGE                     # Limpiar
SAVE / SAVEAS / OPEN
UNDO (Ctrl+Z) / REDO (Ctrl+Y)
HELP / ABOUT
```

---

## ⌨️ Atajos

| Tecla | Acción |
|-------|--------|
| `L C A P R T D M O X S` | Tools (S=Stretch) |
| `Esc` | Cancelar → command line |
| `Click Der` | Repetir último comando |
| `F2` | Text screen |
| `F7` | Grid toggle |
| `F8` | Ortho toggle |
| `F9` | Snap toggle |
| `↑ ↓` | Historial comandos |
| `Ctrl+Z / Ctrl+Y` | Undo / Redo |
| `Space/Enter` | Ciclar modo grip (stretch→move→rotate→scale) |

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 163 passed in ~2.0s
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
| `test_scripting/` | DogLISP reader, eval, builtins, REPL |

---

## 🗂️ Estructura Completa

```
cad2d-lite/
├── src/
│   ├── main.py                          # Entry point
│   ├── app.py                           # QApplication + MainWindow
│   ├── model/
│   │   ├── document.py                  # Documento central
│   │   ├── layer.py / layer_manager.py  # Capas
│   │   ├── snap.py                      # SnapEngine + 11 SnapTypes
│   │   ├── sysvars.py                   # 43 variables SETVAR
│   │   ├── aci.py                       # ACI 256 → RGB
│   │   ├── linetype_defs.py             # 15 tipos de línea
│   │   ├── hatch_patterns.py            # 8 patrones
│   │   ├── units.py                     # Unidades
│   │   └── entities/
│   │       ├── base.py                  # CadEntity + Point
│   │       ├── line.py, circle.py, arc.py
│   │       ├── polyline.py, text.py
│   │       ├── dimension.py, point_entity.py
│   │       ├── ellipse.py, block.py
│   │       └── __init__.py
│   ├── view/
│   │   ├── cad_view.py                  # QGraphicsView Y-up
│   │   ├── cad_scene.py                 # QGraphicsScene
│   │   ├── graphics/
│   │   │   ├── entity_items.py          # GfxItems (ACI, linetype, PDMODE)
│   │   │   └── grid_item.py             # Grid visual
│   │   └── ui/
│   │       ├── main_window.py           # Screen menu, command line
│   │       ├── psychedelic_about.py     # Diálogo ABOUT
│   │       └── pug_icon.py              # Icono pug
│   ├── controller/
│   │   ├── tool_manager.py              # Registry + switching
│   │   ├── calc_engine.py               # CALC calculator
│   │   ├── tools/                       # 35 tools
│   │   │   ├── base_tool.py             # Snap, layer, color, transient
│   │   │   ├── select_tool.py           # Selección + GRIPS
│   │   │   ├── line_tool.py → stretch_tool.py
│   │   │   └── ...                      # (35 archivos)
│   │   └── commands/                    # Undo/redo stack
│   ├── scripting/                       # DogLISP 🦎
│   │   ├── reader.py                    # Tokenizer + parser
│   │   ├── eval.py                      # Interpreter
│   │   ├── builtins.py                  # CAD builtins
│   │   └── repl.py                      # REPL
│   └── io/
│       ├── cad_file.py                  # .cadlite JSON
│       ├── dxf_export.py / dxf_import.py # DXF R2010
│       ├── dwg_io.py                    # DWG import bridge
│       ├── minimal_dxf.py               # Minimal DXF writer
│       └── script_engine.py             # .scr runner
├── tests/
│   ├── test_entities/                   # 9 entity tests
│   ├── test_scripting/                  # DogLISP tests
│   ├── test_aci_sysvars.py
│   ├── test_layer.py, test_undo.py
│   ├── test_cad_file.py, test_commands.py
│   └── conftest.py
├── examples/
│   ├── bolt_holes.lsp                   # Lisp: grilla de pernos
│   ├── grid.lsp                         # Lisp: grilla modular
│   ├── spiral.lsp                       # Lisp: espiral
│   ├── cercha_19vanos.py/.scr           # Cercha 19 vanos
│   └── run_cercha.py                    # Launcher
├── docs/
│   ├── index.html                       # Documentación interactiva
│   └── plans/                           # Planes de desarrollo
├── templates/
│   └── truss-generator.py               # Generador .scr
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🎨 UI — Estilo AutoCAD 10

| Elemento | Color |
|----------|-------|
| Fondo | `#000000` |
| Screen menu | `#0000AA` (azul VGA) |
| Grid | `#0a1a2a` |
| Texto | `#FFFFFF` |
| Headers | `#44AAFF` |
| Acento | `#FFCC00` |
| Status bar | `#000088` |
| Crosshair | Blanco alpha 180 |
| Pickbox | `#00FF00` |
| Command cursor | `#00FF00`, 3px, blink |
| Tipografía | Courier New |

---

## 📖 Documentación

Doc interactiva en `docs/index.html` (abrir con `open docs/index.html` o `HELP` en DogCAD):

- **10 capítulos** de manual para novatos (desde "qué es un CAD" hasta DogLISP avanzado)
- **Glosario** de 15 términos, **Troubleshooting** de 9 problemas comunes
- **Referencia rápida** de 60+ comandos con búsqueda en vivo
- **Sidebar TOC** con scroll spy, **secciones colapsibles**
- **Copy-to-clipboard** en bloques de código
- **Modo claro/oscuro** (toggle ☀️/🌙 con localStorage)
- **Print stylesheet** para exportar a PDF
- Easter eggs: Konami → Matrix, DOOM → Infierno, ` → Terminal

---

## 👨‍💻 Autor

**Ing. Giovanni Correa Mejía** — Zipaquirá, Cundinamarca 🇨🇴

Hecho con Python 3.12, PySide6 6.11, ezdxf 1.1, pytest 9.1, pan de sagú y puro vicio ingenieril.

Dedicado a la memoria de AutoCAD R10 (1988) — DOS 3.3, EGA/VGA 640x480, diskettes de 5¼, y el inconfundible screen menu azul.

---

## 📜 Licencia

MIT — dibuje sin miedo, exporte sin culpa, fork sin permiso.
