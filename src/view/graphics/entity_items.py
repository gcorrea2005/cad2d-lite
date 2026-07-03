from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPen, QColor, QPainter
from src.model.entities.line import Line
from src.model.entities.circle import Circle
from src.model.entities.arc import Arc
from src.model.entities.polyline import Polyline
from src.model.entities.text import TextEntity
from src.model.entities.dimension import Dimension
from src.model.entities.point_entity import PointEntity
import math


class GfxLineItem(QGraphicsItem):
    def __init__(self, entity: Line):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self.entity.start.x, self.entity.start.y),
            QPointF(self.entity.end.x, self.entity.end.y),
        )


class GfxCircleItem(QGraphicsItem):
    def __init__(self, entity: Circle):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        r = self.entity.radius
        c = self.entity.center
        painter.drawEllipse(QPointF(c.x, c.y), r, r)


class GfxArcItem(QGraphicsItem):
    def __init__(self, entity: Arc):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        e = self.entity
        # QPainter.drawArc uses 1/16 degree units, and spans counter-clockwise
        span_angle = int(-math.degrees(e.end_angle - e.start_angle) * 16)
        start_angle = int(-math.degrees(e.start_angle) * 16)
        rect = QRectF(
            QPointF(e.center.x - e.radius, e.center.y - e.radius),
            QPointF(e.center.x + e.radius, e.center.y + e.radius),
        )
        painter.drawArc(rect, start_angle, span_angle)


class GfxPolylineItem(QGraphicsItem):
    def __init__(self, entity: Polyline):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        verts = self.entity.vertices
        for i in range(len(verts) - 1):
            painter.drawLine(
                QPointF(verts[i].x, verts[i].y),
                QPointF(verts[i + 1].x, verts[i + 1].y),
            )
        if self.entity.is_closed and len(verts) >= 2:
            painter.drawLine(
                QPointF(verts[-1].x, verts[-1].y),
                QPointF(verts[0].x, verts[0].y),
            )


class GfxTextItem(QGraphicsItem):
    def __init__(self, entity: TextEntity):
        super().__init__()
        self.entity = entity
        self.setZValue(0)
        # Keep text readable at any zoom level
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        font = painter.font()
        # Use pixel size for consistent readability
        font.setPixelSize(max(8, int(self.entity.height * 40)))
        painter.setFont(font)
        painter.drawText(
            QPointF(self.entity.position.x, self.entity.position.y),
            self.entity.content,
        )


class GfxDimensionItem(QGraphicsItem):
    def __init__(self, entity: Dimension):
        super().__init__()
        self.entity = entity
        self.setZValue(0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

    def boundingRect(self) -> QRectF:
        bmin, bmax = self.entity.bounding_box()
        return QRectF(QPointF(bmin.x, bmin.y), QPointF(bmax.x, bmax.y))

    def paint(self, painter: QPainter, option, widget=None):
        e = self.entity
        color = QColor(e.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)

        # Extension lines
        painter.drawLine(
            QPointF(e.def_point1.x, e.def_point1.y),
            QPointF(e.def_point1.x, e.text_position.y),
        )
        painter.drawLine(
            QPointF(e.def_point2.x, e.def_point2.y),
            QPointF(e.def_point2.x, e.text_position.y),
        )
        # Dimension line
        painter.drawLine(
            QPointF(e.def_point1.x, e.text_position.y),
            QPointF(e.def_point2.x, e.text_position.y),
        )
        # Text
        dist = e.measured_distance()
        font = painter.font()
        font.setPixelSize(10)
        painter.setFont(font)
        text = f"{dist:.2f}"
        mid_x = (e.def_point1.x + e.def_point2.x) / 2
        painter.drawText(QPointF(mid_x - 10, e.text_position.y - 2), text)


class GfxPointItem(QGraphicsItem):
    def __init__(self, entity: PointEntity):
        super().__init__()
        self.entity = entity
        self.setZValue(0)

    def boundingRect(self) -> QRectF:
        return QRectF(QPointF(self.entity.position.x - 3, self.entity.position.y - 3),
                      QPointF(self.entity.position.x + 3, self.entity.position.y + 3))

    def paint(self, painter: QPainter, option, widget=None):
        color = QColor(self.entity.color)
        pen = QPen(color)
        pen.setWidthF(0)
        painter.setPen(pen)
        p = self.entity.position
        painter.drawLine(QPointF(p.x - 2, p.y - 2), QPointF(p.x + 2, p.y + 2))
        painter.drawLine(QPointF(p.x + 2, p.y - 2), QPointF(p.x - 2, p.y + 2))
