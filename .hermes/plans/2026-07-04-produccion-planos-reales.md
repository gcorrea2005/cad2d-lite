# DogCAD 2D Lite — Plan de Producción: Planos Reales

> *"Del juguete retro al escritorio del ingeniero civil"*
> Fecha: 2026-07-04 | Tests: 99/99 ✅

---

## FASE 0 — LO QUE YA TENEMOS (base sólida)

- 30 tools dibujo/modificación ✅
- 99 tests ✅
- 11 modos OSNAP con prioridad ✅
- 43 SETVAR (OSMODE, PDMODE, PDSIZE, CECOLOR, FILLETRAD...) ✅
- ACI 256 colores ✅
- Crosshair + pickbox ✅
- Command history + ESC → cmd line ✅
- Status bar (LAYER/COLOR/LINETYPE/coords/FILE) ✅
- CLAYER sincronizado ✅

---

## PRIORIDADES PARA PRODUCIR PLANOS REALES

### 🔴 BLOQUE A — IMPRESCINDIBLE (sin esto no se puede entregar un plano)

#### A1. DIMENSIONES COMPLETAS (4h)
```
DIMALIGNED    → cota paralela a los puntos (no solo H/V)
DIMRADIUS     → cota de radio (R 5.00)
DIMDIAMETER   → cota de diámetro (⌀ 10.00)
DIMANGULAR    → cota de ángulo (45°)
DIMBASELINE   → cotas apiladas desde una base
DIMCONTINUE   → cotas encadenadas
```
**Por qué:** sin cotas alineadas y de radio, un plano arquitectónico no sirve.

#### A2. ESTILOS DE TEXTO (2h)
```
STYLE command    → crear/modificar estilos de texto
TEXT height      → heredar de TEXTSIZE
MTEXT            → texto multilínea (párrafos)
Justificación    → left/center/right/middle
Font             → soporte para .shx o system fonts
```
**Por qué:** las notas y rótulos son el 30% de un plano.

#### A3. TIPOS DE LÍNEA (2h)
```
LINETYPE command → cargar/definir tipos de línea
DASHED           → - - - - (líneas ocultas)
CENTER           → -- -- -- (ejes)
HIDDEN           → _ _ _ _ (elementos ocultos)
PHANTOM          → -- -- -- (proyecciones)
DASHDOT          → -.-.-.- (cortes)
LTSCALE          → escala global (SETVAR ya existe)
CELTYPE          → tipo de línea actual (SETVAR ya existe)
```
**Por qué:** sin tipos de línea no se distinguen ejes, muros ocultos, proyecciones.

#### A4. DXF IMPORT (2h)
```
DXFIN command    → importar .dxf (ezdxf.readfile)
Mapeo entidades  → LINE, CIRCLE, ARC, POLYLINE, TEXT, DIMENSION
Mapeo capas      → layer names del DXF → LayerManager
Mapeo colores    → ACI del DXF → ACI nuestro
```
**Por qué:** todo ingeniero tiene planos en DXF. Sin import no hay interoperabilidad.

---

### 🟠 BLOQUE B — NECESARIO (calidad profesional)

#### B1. PLOT / IMPRESIÓN A ESCALA (3h)
```
PLOT command       → exportar viewport actual a PDF
Escala             → 1:50, 1:100, 1:200, fit to paper
Paper sizes        → A4, A3, A2, A1, A0
CTB/estilos plot   → grosor de línea por color ACI
Ventana de plot    → seleccionar área rectangular
```
**Por qué:** un plano que no se puede imprimir no es un plano.

#### B2. HATCH PATTERNS (3h)
```
ANSI31 → ladrillo/mampostería (/////)
ANSI32 → acero estructural (XXXX)
ANSI33 → bronce (\\\\\\)
ANSI34 → plástico/caucho
ANSI35 → concreto (triángulos)
ANSI36 → tierra/relleno
AR-CONC → concreto arquitectónico
EARTH   → tierra compactada
```
**Por qué:** los materiales se identifican por el hatch en corte.

#### B3. BLOQUES (4h)
```
BLOCK command    → definir bloque (nombre + punto base + entidades)
INSERT command   → insertar bloque (escala, rotación)
WBLOCK command   → exportar bloque a archivo .cadlite
Explode bloques  → EXPLODE ya existe, adaptarlo
```
**Por qué:** puertas, ventanas, muebles, símbolos eléctricos son bloques.

#### B4. BIBLIOTECA DE BLOQUES BÁSICOS (1h)
```
Puerta 80cm       → arco + línea
Puerta 90cm       → arco + línea
Ventana 1m        → 4 líneas paralelas
Ventana 2m        → 4 líneas paralelas
Inodoro           → polilínea
Lavamanos         → círculo + rectángulo
Símbolo luz       → círculo con cruz
Tomacorriente     → semicírculo con líneas
```
**Por qué:** sin bloques predefinidos, dibujar es lentísimo.

---

### 🟡 BLOQUE C — CALIDAD DE VIDA (productividad diaria)

#### C1. GRID + SNAP A REJILLA (2h)
```
F7 → toggle GRID visual (dots)
F9 → toggle SNAP a grid (fuerza cursor a puntos)
GRIDUNIT → espaciado (SETVAR ya existe)
SNAPUNIT → incremento (SETVAR ya existe)
```
**Por qué:** para dibujar muros a 15cm, snap a grid es indispensable.

#### C2. COORDENADAS RELATIVAS Y POLARES (1h)
```
@100,0      → 100 unidades en X desde último punto
@200<45     → 200 unidades a 45° desde último punto
LASTPOINT   → se actualiza al dibujar (SETVAR ya existe)
```
**Por qué:** sin coordenadas relativas, dibujar es un dolor.

#### C3. UNIDADES ARQUITECTÓNICAS (1h)
```
UNITS command  → meters, centimeters, millimeters, inches
LUNITS=2       → decimal (SETVAR ya existe)
LUPREC=2       → 2 decimales = centímetros
Formato en UI  → mostrar 1.50 en vez de 1.5000
```
**Por qué:** el ingeniero piensa en metros y centímetros.

#### C4. CAPAS PREDEFINIDAS (30min)
```
LAYER template con:
0           → blanco, CONTINUOUS
MUROS       → cyan, CONTINUOUS  
PUERTAS     → yellow, CONTINUOUS
VENTANAS    → green, CONTINUOUS
COTAS       → red, CONTINUOUS
TEXTO       → white, CONTINUOUS
EJES        → red, CENTER
MOBILIARIO  → gray, CONTINUOUS
ELECTRICO   → blue, CONTINUOUS
SANITARIO   → magenta, CONTINUOUS
```
**Por qué:** estándares de capas organizan el drawing.

---

### 🟢 BLOQUE D — NICE TO HAVE

#### D1. TRIM/EXTEND entre múltiples entidades
#### D2. FILLET con radio 0 (esquina viva)
#### D3. CHAMFER con distancia
#### D4. STRETCH (con ventana de selección)
#### D5. GRIPS para editar entidades con el mouse
#### D6. REGEN automático
#### D7. Autosave (SAVETIME SETVAR ya existe)
#### D8. Backup (.bak)

---

## ORDEN DE ATAQUE HOY

| # | Qué | Tiempo | Impacto |
|---|-----|--------|---------|
| 1 | DIMALIGNED + DIMRADIUS | 1.5h | ⭐⭐⭐⭐⭐ |
| 2 | LINETYPE (DASHED, CENTER, HIDDEN) | 1.5h | ⭐⭐⭐⭐⭐ |
| 3 | Coordenadas relativas/polares | 45min | ⭐⭐⭐⭐ |
| 4 | Capas predefinidas (template) | 30min | ⭐⭐⭐⭐ |
| 5 | DXF IN | 2h | ⭐⭐⭐⭐⭐ |
| 6 | Bloques básicos + BLOCK/INSERT | 3h | ⭐⭐⭐⭐ |
| 7 | PLOT a PDF con escala | 2h | ⭐⭐⭐⭐⭐ |
| 8 | HATCH patterns | 2h | ⭐⭐⭐ |
| 9 | GRID visual + SNAP grid | 1.5h | ⭐⭐⭐ |
| 10 | Unidades arquitectónicas | 45min | ⭐⭐ |

**Total: ~15h de trabajo para producción real**

---

## HOY SUGERIDO (sesión actual)

```
1. LINETYPE + CELTYPE → tipos de línea visibles YA
2. DIMALIGNED + DIMRADIUS → cotas reales YA  
3. Coordenadas @ → dibujar con precisión YA
4. Capas template → organización YA
```

**~4h de trabajo → resultado: plano arquitectónico básico funcional**
