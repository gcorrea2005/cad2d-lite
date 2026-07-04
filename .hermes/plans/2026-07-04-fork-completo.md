# DogCAD 2D Lite — Plan Fork Completo AutoCAD R10
# 2026-07-04 | 99 tests | 7,810 líneas | 94 archivos

## LO QUE YA FUNCIONA
- 30 herramientas DRAW/MODIFY/DISPLAY/INQUIRY
- 43 SETVAR, 11 OSNAP, ACI 256, 15 linetypes
- Capas, BYLAYER, CLAYER, TEMPLATE
- PLOT PDF, DXF IN, SCRIPT
- Screen menu, cmd line + history, status bar
- Coordenadas @ relativas/polares

## LO QUE FALTA PARA PRODUCIR PLANOS REALES

### FASE 1 — DIM (prioridad #1)
- [ ] DIMLINEAR con texto real (no solo línea)
- [ ] DIMALIGNED funcional completo
- [ ] DIMRADIUS mostrar R + valor real
- [ ] DIMDIAMETER mostrar ⌀ + valor
- [ ] DIMANGULAR con arco y grados
- [ ] DIMBASELINE (cadena de cotas)
- [ ] Flechas en puntas de cota (tick/arrow)
- [ ] Texto centrado/rotado en la línea de cota

### FASE 2 — DXF IN real
- [ ] Manejar LWPOLYLINE con arcos
- [ ] Manejar bloques INSERT (como group)
- [ ] Preservar capas y colores del DXF
- [ ] SPLINE → polyline aproximada
- [ ] Hatch boundary import

### FASE 3 — HATCH real
- [ ] ANSI31 ladrillo, ANSI32 acero, ANSI35 concreto
- [ ] Detección de boundary (click en área cerrada)
- [ ] SOLID fill (ya existe, revisar)
- [ ] Escala de hatch (HPSCALE)

### FASE 4 — BLOQUES
- [ ] BLOCK (crear bloque de entidades seleccionadas)
- [ ] INSERT (insertar bloque con escala/rotación)
- [ ] WBLOCK (exportar bloque a archivo)
- [ ] Biblioteca básica: puerta, ventana, lavamanos

### FASE 5 — PLOT profesional
- [ ] Scale 1:50, 1:100, 1:200 reales
- [ ] Layout paper space (margen, título)
- [ ] Plot window (seleccionar área)
- [ ] CTB/estilos de pluma (grosor por color)

### FASE 6 — Unidades y precisión
- [ ] UNITS comando funcional
- [ ] Arquitectónicas (pies/pulgadas)
- [ ] Métricas (m, cm, mm)
- [ ] LUPREC afecta display de coordenadas
- [ ] DIST/AREA muestran unidades

### FASE 7 — GRIPS y selección
- [ ] STRETCH con grips en endpoints/midpoints
- [ ] Selección por ventana (window/crossing)
- [ ] Selección múltiple con Shift
- [ ] GRIPS para MOVE/ROTATE/SCALE directo

### FASE 8 — Pulido final
- [ ] DONUT (ya tiene esqueleto)
- [ ] ELLIPSE
- [ ] TABLET (digitalizadora)
- [ ] Autosave cada 5 minutos
- [ ] Backup .bak al guardar

## ORDEN DE ATAQUE (HOY)
1. DIM — terminar cotas (flechas, texto, alineación)
2. UNITS — que las coordenadas muestren metros
3. GRIPS — edición directa sin comandos
4. BLOQUES — puertas y ventanas repetibles

## NO MÁS DISTRACCIONES
- ❌ HTML maquillaje
- ❌ Easter eggs nuevos
- ❌ Refactors cosméticos
- ✅ Solo features que producen planos
