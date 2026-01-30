from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QGraphicsView, QGraphicsScene,
    QGraphicsItem
)
from PySide6.QtGui import QBrush, QPen, QColor
from PySide6.QtCore import QRectF, Qt
import sys


class Node(QGraphicsItem):
    def __init__(self, title="Node"):
        super().__init__()
        self.width = 160
        self.height = 80
        self.title = title

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRoundedRect(
            0, 0, self.width, self.height, 8, 8
        )

        painter.setPen(Qt.white)
        painter.drawText(10, 25, self.title)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Node Test")
        self.resize(800, 600)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-400, -300, 800, 600)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        node = Node("Hello Node")
        self.scene.addItem(node)
        node.setPos(0, 0)


app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec())
