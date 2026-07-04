"""
Psychedelic About dialog for CAD 2D Lite.
Rainbow cycling, matrix rain, CRT flicker, trippy vibes.
"""
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QLinearGradient
import math
import random


class PsychedelicAbout(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ACERCA DE — CAD 2D Lite")
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: #000010;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._hue = 0.0
        self._particles: list[tuple[float, float, float, float]] = []
        for _ in range(120):
            self._particles.append((
                random.uniform(0, 500),
                random.uniform(0, 350),
                random.uniform(2, 8),
                random.uniform(0, 360),
            ))
        self._matrix_cols: list[tuple[int, float, str]] = []
        for x in range(0, 500, 12):
            self._matrix_cols.append((x, random.uniform(0, 350), ""))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)  # ~25 fps

        self._close_btn = QPushButton("[ X ]  ESCAPE REALITY", self)
        self._close_btn.setGeometry(150, 310, 200, 30)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: #000033;
                color: #FFCC00;
                border: 1px solid #FF00FF;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #330066;
                color: #00FFFF;
                border: 1px solid #00FFFF;
            }
        """)
        self._close_btn.clicked.connect(self.accept)

    def _tick(self):
        self._hue = (self._hue + 2.5) % 360  # faster rainbow
        # Update matrix rain
        for i, (x, y, _) in enumerate(self._matrix_cols):
            new_y = y + random.uniform(2, 8)
            if new_y > 350:
                new_y = random.uniform(-50, 0)
            char = chr(random.choice([0x30A0 + i for i in range(96)]))  # katakana
            self._matrix_cols[i] = (x, new_y, char)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Rainbow background gradient ──
        grad = QLinearGradient(0, 0, 500, 350)
        for i in range(6):
            t = i / 5.0
            h = (self._hue + i * 60) % 360
            grad.setColorAt(t, QColor.fromHsv(int(h), 200, 40))
        painter.fillRect(self.rect(), grad)

        # ── Matrix rain background ──
        for x, y, char in self._matrix_cols:
            alpha = int(80 + 60 * (y / 350))
            painter.setPen(QColor(0, 255, 0, alpha))
            painter.setFont(QFont("Courier New", 9))
            painter.drawText(int(x), int(y), char)

        # ── Floating particles ──
        for px, py, size, hue in self._particles:
            c = QColor.fromHsv(int((hue + self._hue) % 360), 255, 200, 120)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(int(px), int(py), int(size), int(size))

        # ── Psychedelic title ──
        title_hue = self._hue
        title = "CAD 2D Lite"
        font = QFont("Courier New", 28, QFont.Weight.Bold)
        painter.setFont(font)
        for i, ch in enumerate(title):
            h = (title_hue + i * 20) % 360
            painter.setPen(QColor.fromHsv(int(h), 255, 255))
            painter.drawText(30 + i * 22, 60, ch)

        # ── Subtitle ──
        font2 = QFont("Courier New", 11)
        painter.setFont(font2)

        lines = [
            ("Hecho en Zipaquirá, Cundinamarca 🇨🇴", 90),
            ("con Python, vicio y pan de sagú", 108),
            ("Giovanni Correa © 2026", 130),
            ("30 herramientas · 60 tests · Y+ up", 155),
            ("Stack: PySide6 + ezdxf + pytest", 178),
            ("", 198),
            ("DEDICADO A LA MEMORIA DE:", 220),
            ("AutoCAD R10 (1988) — DOS, EGA/VGA", 242),
            ("y a todos los que dibujaron con grid", 264),
            ("y se quedaron sin RAM.", 282),
        ]
        for text, y in lines:
            h = (title_hue + y * 0.5) % 360
            painter.setPen(QColor.fromHsv(int(h), 200, 255))
            painter.drawText(30, y, text)

        # ── CRT flicker line ──
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        flicker_y = (math.sin(self._hue * 0.1) * 150) + 175
        painter.drawLine(0, int(flicker_y), 500, int(flicker_y))

        # ── Scanlines ──
        painter.setPen(QPen(QColor(0, 0, 0, 25)))
        for y in range(0, 350, 3):
            painter.drawLine(0, y, 500, y)

        painter.end()

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)
