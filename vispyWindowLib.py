from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView,
    QGraphicsScene
)

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QMouseEvent, QColor, QPen, QPainter
from PySide6.QtCore import Qt, QEvent, QLineF

class GraphicsView(QGraphicsView):
    
    def __init__(self, scene):
        super().__init__(scene)

        self.setRenderHint(QPainter.Antialiasing)

        self.setViewportUpdateMode(
            QGraphicsView.FullViewportUpdate
        )

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def wheelEvent(self, event):
        zoom_in = 1.25
        zoom_out = 1/zoom_in
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_out)
        else:
            self.scale(zoom_out, zoom_out)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = QMouseEvent(
                QEvent.MouseButtonPress,
                event.position(),
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            )
            super().mousePressEvent(fake)
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            fake = QMouseEvent(
                QEvent.MouseButtonRelease,
                event.position(),
                Qt.LeftButton,
                Qt.NoButton,
                Qt.NoModifier,
            )
            super().mouseReleaseEvent(fake)
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mouseReleaseEvent(event)
            
    # def drawBackground(self, painter, rect):
    #     super().drawBackground(painter, rect)
        
    #     grid_size = 40
    #     left = int(rect.left()) - (int(rect.left()) % grid_size)
    #     top = int(rect.top()) - (int(rect.top()) % grid_size)
        
    #     lines = []
        
    #     for x in range(left, int(rect.right()), grid_size):
    #         lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            
    #     for y in range(top, int(rect.bottom()), grid_size):
    #         lines.append(QLineF(rect.left(), y, rect.right(), y))
            
    #     painter.setPen(QPen(QColor(60,60,60), 1))
    #     painter.drawLines(lines)
        
class GraphicsScene(QGraphicsScene):
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        grid_size = 40
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        lines = []

        for x in range(left, int(rect.right()), grid_size):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))

        for y in range(top, int(rect.bottom()), grid_size):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawLines(lines)