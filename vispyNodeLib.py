from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyle
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath
from PySide6.QtCore import QRectF, Qt

class Node(QGraphicsItem):
    def __init__(self, title="Node"):
        super().__init__()
        
        self.width = 160
        self.height = 80
        self.title = title
        
        self.sockets = []
        
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )
        
        self.input_socket = Socket(self, 0, 40)
        self.output_socket = Socket(self, self.width, 40)
        
    def boundingRect(self):
        return QRectF(0,0 , self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        
        if option.state & QStyle.State_Selected:
            pen = QPen(QColor(0,170,255),3)
        else:
            pen = QPen(Qt.black, 2)
            
        painter.setPen(pen)
        painter.setBrush(QColor(45,45,45))
        
        painter.drawRoundedRect(
            0,0 , self.width, self.height, 6,6
        )
        
        painter.setPen(Qt.white)
        painter.drawText(10,20, self.title)
        
    def itemChange(self, change, value):
        if change == QGraphicsPathItem.ItemPositionHasChanged:
            for socket in self.sockets:
                for edge in socket.edges:
                    edge.update_path()
        return super().itemChange(change, value)
        
        
class Socket(QGraphicsItem):
    def __init__(self,parent,x,y):
        super().__init__(parent)
        self.radius = 6
        self.setPos(x,y)
        
        self.edges = []
        
    def boundingRect(self):
        return QRectF(
            -self.radius,
            -self.radius,
            self.radius*2,
            self.radius*2
        )
        
    def paint(self, painter, option, widget=None):
        painter.setBrush(QColor(200,200,200))
        painter.drawEllipse(self.boundingRect())
        
        
class Edge(QGraphicsPathItem):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.update_path()
        
        self.setPen(QPen(QColor(255,255,255),2))
        self.setPen(QPen(QColor(220,220,220),2.5))
        
    def update_path(self):
        path = QPainterPath()
        p1 = self.start.scenePos()
        p2 = self.end.scenePos()
        
        path.moveTo(p1)
        dx = (p2.x() - p1.x()) * 0.5
        path.cubicTo(
            p1.x() + dx, p1.y(),
            p2.x() - dx, p2.y(),
            p2.x(), p2.y()
        )
        self.setPath(path)