"""Generador de .scr para cercha de 19 vanos (anchores variables).
Usar: .venv/bin/python examples/cercha_19vanos.py
Luego en DogCAD: SCRIPT -> examples/cercha_19vanos.scr

Configuración:
  7×900 + 825 + 4×900 + 825 + 5×900 + 470  (mm)
  Diagonales mismo sentido, se invierten en vano 10.
"""
import math

H = 1000.0  # altura de cercha (mm)

# Anchores de cada vano [mm] — 19 vanos
ANCHOS = [900]*7 + [825] + [900]*4 + [825] + [900]*5 + [470]

N = len(ANCHOS)  # 19

# Calcular coordenadas X de cada nudo (N+1 nudos)
xs = [0.0]
for a in ANCHOS:
    xs.append(xs[-1] + a)

ancho_total = xs[-1]

lines = []
lines.append("LAYER NEW CERCHA")
lines.append("LAYER SET CERCHA")

# Cuerda superior
pts_top = [f"{x},{H}" for x in xs]
lines.append(f"PLINE {' '.join(pts_top)}")

# Cuerda inferior
pts_bot = [f"{x},0" for x in xs]
lines.append(f"PLINE {' '.join(pts_bot)}")

# Montantes verticales
for x in xs:
    lines.append(f"LINE {x},0 {x},{H}")

# Diagonales
# Vanos 1-10 (indices 0-9): arriba-izq → abajo-der
# Vanos 11-19 (indices 10-18): invertidas (abajo-izq → arriba-der)
for i in range(N):
    x1 = xs[i]
    x2 = xs[i + 1]
    if i < 10:  # vanos 1..10
        lines.append(f"LINE {x1},{H} {x2},0")
    else:        # vanos 11..19
        lines.append(f"LINE {x1},0 {x2},{H}")

OFFSET = 5000
x_min = -OFFSET
y_min = -OFFSET
x_max = ancho_total + OFFSET
y_max = H + OFFSET
lines.append(f"LIMITS {x_min},{y_min} {x_max},{y_max}")
lines.append("ZOOM E")
lines.append(f"; Cercha {N} vanos — {ancho_total:.0f}×{H:.0f}mm")
lines.append(f"; Anchores: {ANCHOS}")
lines.append(f"; Diagonales vanos 1-10 abajo, vanos 11-19 arriba")

scr_content = "\n".join(lines) + "\n"

with open(__file__.replace(".py", ".scr"), "w") as f:
    f.write(scr_content)

print(f"✅ Cercha generada: {N} vanos, {ancho_total:.0f}mm ancho x {H:.0f}mm alto")
print(f"   Anchores: {ANCHOS}")
print(f"   Archivo: {__file__.replace('.py', '.scr')}")
print()
print("Para cargar en DogCAD:")
print("   1. Menu FILE -> SCRIPT")
print("   2. Seleccionar el archivo .scr")
