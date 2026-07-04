"""
Pixel-art pug icon for DogCAD 2D Lite.  🐾🐶
"""
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont, QIcon
from PySide6.QtCore import Qt, QRect, QPoint


def create_pug_icon() -> QIcon:
    """Draw a retro pixel-art pug face; return QIcon(128×128)."""
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#000000"))             # black background

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # crisp pixel edges

    # ── body (roundish square) ──
    body_color = QColor("#D4A574")             # fawn pug
    painter.setBrush(QBrush(body_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(10, 16, 108, 102, 32, 32)

    # ── ears (dark, floppy) ──
    ear_color = QColor("#3B2F2F")
    painter.setBrush(QBrush(ear_color))
    painter.drawEllipse(6, 12, 32, 50)          # left ear
    painter.drawEllipse(90, 12, 32, 50)         # right ear

    # ── forehead wrinkles ──
    wrinkle_color = QColor("#B8956A")
    painter.setBrush(Qt.BrushStyle.NoBrush)
    pen = QPen(wrinkle_color, 2)
    painter.setPen(pen)
    painter.drawArc(QRect(36, 32, 56, 24), 0 * 16, 180 * 16)
    painter.drawArc(QRect(38, 44, 52, 20), 0 * 16, 180 * 16)
    painter.drawArc(QRect(40, 54, 48, 18), 0 * 16, 180 * 16)

    # ── eyes (big, dark, glossy) ──
    eye_white = QColor("#F5F5F0")
    eye_pupil = QColor("#1A1A2E")
    eye_spark = QColor("#FFFFFF")

    for cx in [42, 86]:
        # white
        painter.setBrush(QBrush(eye_white))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(cx, 74), 14, 16)
        # pupil
        painter.setBrush(QBrush(eye_pupil))
        painter.drawEllipse(QPoint(cx, 72), 8, 10)
        # spark highlight
        painter.setBrush(QBrush(eye_spark))
        painter.drawEllipse(QPoint(cx + 3, 66), 3, 3)

    # ── muzzle (darker flat area) ──
    muzzle_color = QColor("#5C4A3A")
    painter.setBrush(QBrush(muzzle_color))
    painter.drawRoundedRect(40, 94, 48, 28, 12, 12)

    # ── nose (black, central) ──
    painter.setBrush(QBrush(QColor("#1A1A1A")))
    painter.drawEllipse(QPoint(64, 100), 7, 5)

    # ── mouth ──
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor("#2A1F1A"), 2))
    # split under nose
    painter.drawLine(64, 105, 64, 114)
    # smile curves
    painter.drawArc(QRect(48, 108, 16, 10), 180 * 16, 180 * 16)   # left smile
    painter.drawArc(QRect(64, 108, 16, 10), 180 * 16, 180 * 16)   # right smile

    # ── tongue 👅 ──
    tongue_color = QColor("#FF6B8A")
    painter.setBrush(QBrush(tongue_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(54, 112, 20, 10, 5, 5)

    # ── "PUG" badge pixel corner ──
    font = QFont("Courier New", 10, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#FFCC00"))
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, "PUG")

    painter.end()
    return QIcon(pixmap)
