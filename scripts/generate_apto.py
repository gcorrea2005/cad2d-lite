"""
Generate a 66m² apartment floor plan for DogCAD 2D Lite.
2 bedrooms, 2 bathrooms, kitchen, living/dining, terrace.

Layout (~11m x 6m = 66m²):

    +-------+-------+-------+-------------------+
    | BEDRM1| BATH1 |       |                   |
    | 3.5x3 | 2.0x2 |       |     TERRACE       |
    |       |       |  KIT  |     1.2 x 11      |
    +---------------+  3x2  |                   |
    |               +-------+-------------------+
    |   LIVING /    |               |           |
    |   DINING      |    BEDROOM 2  |           |
    |   5.5 x 4     |    3.0 x 3.0  |           |
    |               |               |           |
    |               +-------+-------+           |
    |               | BATH2 |                   |
    |               | 2.0x2 |                   |
    +---------------+---------------+-----------+

Scale: 1 unit = 1 meter
Origin at bottom-left of apartment.
"""

from src.model.document import Document
from src.model.entities.line import Line
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from src.model.entities.base import Point
from src.io.cad_file import save_document
from pathlib import Path

doc = Document()
doc.layer_manager.add_layer("WALLS", "#FFFFFF")
doc.layer_manager.add_layer("DOORS", "#FFCC00")
doc.layer_manager.add_layer("WINDOWS", "#44AAFF")
doc.layer_manager.add_layer("TEXT", "#88FF88")
doc.layer_manager.add_layer("DIMS", "#888888")
doc.layer_manager.set_current("WALLS")

# ===== DIMENSIONS =====
# Apartment: 11m wide x 6m deep = 66m²
# Terrace: 1.2m deep along top
# Interior: 4.8m deep

APT_W = 11.0
APT_D = 6.0
TERRACE_D = 1.2
INT_D = APT_D - TERRACE_D  # 4.8m

# Column positions (X):
# Layout from left to right:
# | BEDRM1 (3.5) | BATH1 (2.0) | KITCHEN (3.0) | BEDRM2 (2.5) |
# |              |             |               |               |
# Below: LIVING + BATH2
X0 = 0.0
X1 = 3.5  # BEDRM1 right
X2 = 5.5  # BATH1 right
X3 = 8.5  # KITCHEN right
X4 = 11.0 # APT right edge

# Row positions (Y):
Y0 = 0.0
Y1 = 4.0  # living/bedrm2 bottom wall
Y2 = 4.8  # interior/terrace boundary  (4.0 + 0.8 hallway? No, let me simplify)

# Simplified: 
# Y0=0 (bottom), Y1=4.0 (split between bedrm2/living lower half and upper), 
# Y2=4.8 (interior top = terrace bottom)
# Wait, this doesn't match. Let me think again.

# Better layout:
# Total depth = 6.0m. Terrace = 1.2m along top. Interior = 4.8m.
# Row Y=0 is bottom, Y=4.8 is interior ceiling, Y=6.0 is terrace railing.
# Split interior vertically at Y=2.8:
# Bottom section: LIVING (left 8.5m) + BEDRM2 + BATH2 (right 2.5m)
# Top section: BEDRM1 (3.5) + BATH1 (2.0) + KITCHEN (3.0) + corridor (2.5)

Y0 = 0.0     # bottom
Y1 = 2.8     # interior split
Y2 = 4.8     # interior top / terrace bottom
Y3 = 6.0     # terrace top

# ===== EXTERIOR WALLS =====
# Outer walls (thick = double line, offset 0.15 each side)
WT = 0.15  # half wall thickness

def wall_line(x1, y1, x2, y2):
    """Add a wall line."""
    doc.add_entity(Line(Point(x1, y1), Point(x2, y2), layer_name="WALLS"))

def double_wall(x1, y1, x2, y2):
    """Create a double-line wall."""
    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy)**0.5
    if length < 0.001:
        return
    nx = -dy / length * WT
    ny = dx / length * WT
    wall_line(x1 + nx, y1 + ny, x2 + nx, y2 + ny)
    wall_line(x1 - nx, y1 - ny, x2 - nx, y2 - ny)

# Exterior perimeter (double walls)
# Bottom
double_wall(X0, Y0, X4, Y0)
# Top (terrace edge)
double_wall(X0, Y3, X4, Y3)
# Left
double_wall(X0, Y0, X0, Y3)
# Right
double_wall(X4, Y0, X4, Y3)

# ===== INTERIOR WALLS (single lines for clarity) =====
# Vertical walls
wall_line(X1, Y0, X1, Y2)   # BEDRM1 right wall
wall_line(X2, Y1, X2, Y3)   # BATH1 right wall
wall_line(X3, Y0, X3, Y2)   # KITCHEN right wall

# Horizontal walls
wall_line(X0, Y1, X3, Y1)   # living/bedrm split (top of lower section)
wall_line(X0, Y2, X4, Y2)   # interior/terrace boundary

# BATH2 walls
wall_line(X3, Y0, X3, Y1)   # BATH2 left
wall_line(X3, Y1, X4, Y1)   # BATH2 top (inline with living split)

# ===== DOOR OPENINGS (gaps in walls) =====
# We'll draw them as small arcs or gaps
def door(x, y, angle=0.0):
    """Draw a door as an arc (swing) + line."""
    import math
    door_w = 0.9
    r = door_w
    c = Point(x + r * math.cos(angle + math.pi), y + r * math.sin(angle + math.pi))
    sa = angle
    ea = angle + math.pi / 2
    # Simple line for door
    dx = math.cos(angle)
    dy = math.sin(angle)
    doc.add_entity(Line(
        Point(x, y),
        Point(x + door_w * dx, y + door_w * dy),
        layer_name="DOORS"))

# Doors
door(1.5, Y0, 0.0)              # BEDRM1 entrance (bottom)
door(3.0, Y1 + 0.1, 0.0)        # BATH1 door
door(6.5, Y0, 0.0)               # KITCHEN entrance
door(X2 + 0.3, Y1 + 0.1, 0.0)   # BEDRM2 door
door(X3 + 0.5, Y0, 0.0)         # BATH2 door
door(X2 - 0.5, Y2, 0.0)         # Terrace door from kitchen

# ===== WINDOWS (thin lines on exterior walls) =====
def window(x1, y1, x2, y2):
    """Draw a window."""
    doc.add_entity(Line(Point(x1, y1), Point(x2, y2), layer_name="WINDOWS"))

# BEDRM1 window (left wall, bottom section)
window(X0, 0.5, X0, 2.0)
# LIVING window (bottom wall, left)
window(4.0, Y0, 7.0, Y0)
# BEDRM2 window (right wall, upper section)
window(X4, 2.0, X4, 4.0)
# KITCHEN window (top wall, above kitchen)
window(5.8, Y2, 8.0, Y2)

# ===== TEXT LABELS =====
def label(x, y, text, size=0.3):
    """Add a text label centered at (x,y)."""
    doc.add_entity(TextEntity(
        Point(x, y), text, height=size, layer_name="TEXT"))

label(1.75, 1.4, "BEDROOM 1", 0.30)
label(4.5, 1.4, "BATH 1", 0.25)
label(7.0, 3.6, "KITCHEN", 0.28)
label(9.75, 1.4, "BEDROOM 2", 0.28)
label(9.75, 3.6, "BATH 2", 0.25)
label(3.5, 0.6, "LIVING / DINING", 0.32)
label(5.5, 5.4, "TERRACE", 0.30)

# ===== DIMENSIONS =====
def dim_line(p1, p2, text_y):
    """Add a linear dimension."""
    mid = Point((p1.x + p2.x) / 2, text_y)
    doc.add_entity(Dimension(p1, p2, mid, layer_name="DIMS"))

# Overall dimensions (outside the building)
off = 0.8  # offset for dimension lines
dim_line(Point(X0, Y0 - off), Point(X4, Y0 - off), Y0 - off - 0.3)
dim_line(Point(X0 - off, Y0), Point(X0 - off, Y3), X0 - off - 0.3)

# Room dimensions
dim_line(Point(X0, Y2 + 0.3), Point(X1, Y2 + 0.3), Y2 + 0.6)   # BEDRM1 width
dim_line(Point(X1 + 0.2, Y2 + 0.3), Point(X2 + 0.2, Y2 + 0.3), Y2 + 0.6)  # BATH1 width
dim_line(Point(X2 + 0.2, Y1 + 0.15), Point(X3 + 0.2, Y1 + 0.15), Y1 + 0.45)  # KITCHEN width

# ===== TERRACE RAILING =====
# Dashed line for terrace edge
for i in range(0, 22):
    x = i * 0.5
    if x + 0.3 <= X4:
        doc.add_entity(Line(Point(x, Y2), Point(x + 0.3, Y2), layer_name="WINDOWS"))

# ===== SAVE =====
out_path = Path("/Users/gcorrea/Documents/12-cad-lite/apto_66m2.cadlite")
save_document(doc, out_path)
print(f"Saved: {out_path}")
print(f"Entities: {len(doc.entities)}")
print(f"Layers: {list(doc.layer_manager.layers.keys())}")
