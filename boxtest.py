# Proof of concept goes here:

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView,
    QGraphicsScene
)

from PySide6.QtCore import Qt
import sys

import vispyNodeLib as vnl
import vispyWindowLib as vwl

class NodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Vispy Proof of Concept")
        self.resize(900,600)
        
        self.scene = vwl.GraphicsScene()
        self.scene.setSceneRect(-400,-300,800,600)
        self.view = vwl.GraphicsView(self.scene)
        
        self.view.setRenderHint(self.view.renderHints())
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        self.setCentralWidget(self.view)
        
        # instantiate a node
        node1 = vnl.Node("Input")
        node2 = vnl.Node("Multiply")
        
        self.scene.addItem(node1)
        self.scene.addItem(node2)
        
        node1.setPos(20,200)
        node2.setPos(200, 0)
        
        edge = vnl.Edge(node1.output_socket, node2.input_socket)
        node1.input_socket.edges.append(edge)
        node2.output_socket.edges.append(edge)
        self.scene.addItem(edge)
        
app = QApplication(sys.argv)
window = NodeEditor()
window.show()
sys.exit(app.exec())

