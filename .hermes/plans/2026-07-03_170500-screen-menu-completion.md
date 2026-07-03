# CAD 2D Lite — Screen Menu Completion Plan

> **For Hermes:** Greenfield execution pattern — write foundations myself, parallelize independent tools, batch tests.

**Goal:** Implement the remaining screen menu items mapped as `ni_*` placeholders.

**Architecture:** Follow existing tool pattern — each command becomes a `BaseTool` subclass or a method on `MainWindow`. Modify tools add `ModifyEntityCommand` undo entries.

**Tech Stack:** Python 3.12, PySide6, ezdxf, pytest (60 tests baseline)

---

## Phase A — Quick Wins (Layer + Display + Inquiry) — ~20 min

### A1. ZOOM P (Previous Zoom)
**File:** `src/view/cad_view.py` — add zoom history stack
- Add `_zoom_stack: list` and `_zoom_index: int` to CadView
- Push current viewport rect on every zoom/pan
- `zoom_previous()` pops and restores
- Wire `ni_ZOOM_P` → `zoom_previous` action

### A2. Inquiry: ID
**Method:** `MainWindow._on_id()` — echo coords of picked point
- Click entity → show type, layer, coords, uuid
- Uses existing `_snap()` for precision

### A3. Inquiry: STATUS
**Method:** `MainWindow._on_status()` — drawing statistics
- Echo: entity count, layer count, limits, current layer, snap/ortho state

### A4. Inquiry: AREA
**File:** `src/controller/tools/area_tool.py` — click polygon vertices, show area
- Multi-click to define polygon boundary
- Right-click/Enter to finish
- Echo area and perimeter

---

## Phase B — Modify Tools (Core) — ~40 min

### B1. MIRROR
**File:** `src/controller/tools/mirror_tool.py`
- Select entities first, then 2 clicks to define mirror axis
- Reflect points across line using geometry math
- Undoable via ModifyEntityCommand

### B2. OFFSET
**File:** `src/controller/tools/offset_tool.py`
- Click a Line/Polyline entity
- Specify offset distance (QInputDialog or click)
- Create parallel copy at distance
- Direction: click side to offset toward

### B3. TRIM
**File:** `src/controller/tools/trim_tool.py`
- Click cutting edge(s), then click segments to trim
- Find intersection between lines, shorten to intersection
- Handles Line-Line intersections

### B4. EXTEND
**File:** `src/controller/tools/extend_tool.py`
- Click boundary edge, then click lines to extend
- Extend line endpoint to meet boundary

### B5. SCALE
**File:** `src/controller/tools/scale_tool.py`
- Select entities, click base point, specify scale factor
- Or: base point + reference length + new length

### B6. FILLET
**File:** `src/controller/tools/fillet_tool.py`
- Click two lines, specify radius
- Compute tangent arc, trim lines to arc endpoints

### B7. CHAMFER
**File:** `src/controller/tools/chamfer_tool.py`
- Click two lines, specify distances
- Compute chamfer line, trim lines

---

## Phase C — More Tools — ~30 min

### C1. BREAK
**File:** `src/controller/tools/break_tool.py`
- Click entity at break point → split into two entities
- Line → two Lines, Polyline → two Polylines

### C2. EXPLODE
**Method:** `MainWindow._on_explode()`
- Polyline → separate Line entities
- Removes original, adds components

### C3. ARRAY (Rectangular)
**File:** `src/controller/tools/array_tool.py`
- Select entities, specify rows/cols/spacing
- Clone entities in grid pattern

### C4. HATCH (basic)
**File:** `src/controller/tools/hatch_tool.py`
- Click inside closed polyline boundary
- Fill with parallel lines pattern
- Create Hatch entity (new entity type)

### C5. PURGE
**Method:** `MainWindow._on_purge()`
- Remove unused (empty) layers
- Echo purged layer names

---

## Phase D — Settings + Polish — ~15 min

### D1. UNITS dialog
**Method:** `MainWindow._on_units()`
- QDialog with precision, angle format, unit type
- Store in document settings

### D2. LIMITS
**Method:** `MainWindow._on_limits()`
- Set drawing limits (min/max coordinates)
- Adjust grid to new limits

### D3. POINT entity
**File:** `src/model/entities/point_entity.py`
- Simple Point entity with position
- `GfxPointItem` for rendering (small cross/X)
- `PointTool` for placing

### D4. PLOT stub
**Method:** `MainWindow._on_plot()`
- Opens print dialog via QPrintDialog
- Renders current view to printer/PDF

---

## Priority Order

| # | Item | Effort | Impact | Phase |
|---|------|--------|--------|-------|
| 1 | OFFSET | Medium | High — core CAD | B2 |
| 2 | MIRROR | Medium | High — core CAD | B1 |
| 3 | TRIM | Hard | High — core CAD | B3 |
| 4 | EXTEND | Medium | High — core CAD | B4 |
| 5 | SCALE | Easy | Medium | B5 |
| 6 | FILLET | Hard | Medium | B6 |
| 7 | EXPLODE | Easy | Medium | C2 |
| 8 | BREAK | Medium | Medium | C1 |
| 9 | AREA | Easy | Medium | A4 |
| 10 | ZOOM P | Easy | Medium | A1 |
| 11 | ID | Easy | Low | A2 |
| 12 | STATUS | Easy | Low | A3 |
| 13 | CHAMFER | Medium | Low | B7 |
| 14 | ARRAY | Medium | Low | C3 |
| 15 | HATCH | Hard | Low | C4 |
| 16 | PURGE | Easy | Low | C5 |
| 17 | UNITS | Easy | Low | D1 |
| 18 | LIMITS | Easy | Low | D2 |
| 19 | POINT | Easy | Low | D3 |
| 20 | PLOT | Medium | Low | D4 |

---

## Execution Strategy

**Phase A** (quick, independent): write directly myself — 4 small items, ~20 min

**Phase B** (modify tools): sequential, each depends on understanding entity geometry
- B1 MIRROR + B5 SCALE first (pure geometry, no intersection math)
- Then B2 OFFSET (line math)
- Then B3 TRIM + B4 EXTEND (intersection math, hardest)
- Then B6 FILLET + B7 CHAMFER (arc/bevel math)

**Phase C** (utility): C2 EXPLODE + C1 BREAK first (entity manipulation), then C5 PURGE, then C3 ARRAY, C4 HATCH last (complex)

**Phase D** (settings): quick standalone items

**Total effort:** ~1.5–2 hours

---

¿Arranco por Phase A (ZOOM P, ID, STATUS, AREA) o prefieres otro orden?
