from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView
)
from PySide6.QtCore import Qt
import sys

import widgets_elements.vispyNodeLib as vnl
import widgets_elements.vispyWindowLib as vwl
import types_classes.node_library as nl

class NodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vispy Proof of Concept")
        self.resize(1200, 900)

        self.scene = vwl.GraphicsScene()
        self.scene.setSceneRect(-50000, -50000, 100000, 100000)

        self.view = vwl.GraphicsView(self.scene)
        self.setCentralWidget(self.view)

app = QApplication(sys.argv)
window = NodeEditor()
window.show()
sys.exit(app.exec())


#56+115+114 