from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit
from PySide6.QtWidgets import QSlider, QProgressBar, QComboBox, QListWidget, QRadioButton, QCheckBox
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Alfie Really Is the Coolest Guy Application")
        
        container = QWidget()
        self.setCentralWidget(container)
        
        layout = QVBoxLayout(container)
        
        label1 = QLabel('Label')
        label1.setAlignment(Qt.AlignCenter)
        
        button = QPushButton("Click")
        
        line_edit = QLineEdit()
        text_edit = QTextEdit()
        
        combobox = QComboBox()
        combobox.addItems(["One", "Two", "Three"])
        
        listwidget = QListWidget()
        listwidget.addItems(["One", "Two", "Three"])
        
        checkbox1 = QCheckBox("One")
        checkbox2 = QCheckBox("Two")
        checkbox3 = QCheckBox("Three")
        
        layout.addWidget(label1)
        layout.addWidget(button)
        layout.addWidget(line_edit)
        layout.addWidget(text_edit)
        layout.addWidget(combobox)
        layout.addWidget(listwidget)
        
        
        
app = QApplication()

window = MainWindow()
window.show()

app.exec()