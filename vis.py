from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QSplitter,
    QMenuBar, QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, qInstallMessageHandler
import sys, os, logging, traceback
import faulthandler

# setup logging to file for crash debugging
_log_path = os.path.join(os.path.dirname(__file__), 'vispy_debug.log')
logging.basicConfig(level=logging.DEBUG, filename=_log_path, filemode='a',
                    format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

# enable faulthandler to dump on fatal errors
try:
    _fh_file = open(_log_path, 'a')
    faulthandler.enable(_fh_file, all_threads=True)
except Exception:
    faulthandler.enable()

# Qt message handler to capture Qt warnings/errors
def _qt_msg_handler(msg_type, context, message):
    try:
        logging.error(f"QtMessage type={msg_type} context={context.file}:{context.line} message={message}")
    except Exception:
        logging.error(f"QtMessage: {message}")

try:
    qInstallMessageHandler(_qt_msg_handler)
except Exception:
    pass

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

        # left side variable manager + main view splitter
        from widgets_elements.vispyWindowLib import VariableManagerWidget
        splitter = QSplitter()
        self.var_manager = VariableManagerWidget(view=self.view)
        splitter.addWidget(self.var_manager)
        splitter.addWidget(self.view)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([260, 940])
        self.setCentralWidget(splitter)

        # Menubar and placeholder actions (Save/Open/etc.) - implement actual functionality later
        self._create_menus()

    def _create_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        new_act = QAction("&New", self)
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self._new_file)
        file_menu.addAction(new_act)

        open_act = QAction("&Open...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self._open_file)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        save_act = QAction("&Save", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self._save_file)
        file_menu.addAction(save_act)

        save_as_act = QAction("Save &As...", self)
        save_as_act.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_act)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(QAction("Undo", self))
        edit_menu.addAction(QAction("Redo", self))

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(QAction("Zoom In", self, shortcut="Ctrl++", triggered=lambda: self.view.scale(1.25, 1.25)))
        view_menu.addAction(QAction("Zoom Out", self, shortcut="Ctrl+-", triggered=lambda: self.view.scale(0.8, 0.8)))

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        prefs_act = QAction("&Preferences...", self)
        prefs_act.triggered.connect(self._show_preferences)
        tools_menu.addAction(prefs_act)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_act = QAction("&About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    # Placeholder handlers for menu actions - to be implemented by you
    def _new_file(self):
        logging.info("New file action triggered")
        QMessageBox.information(self, "New", "Create new file - not implemented yet")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Vispy Files (*.vp *.json);;All Files (*)")
        if path:
            try:
                import savesystem as ss
                ss.load_scene_from_file(self.scene, path)
                logging.info(f"Open file: {path}")
                QMessageBox.information(self, "Open", f"Loaded: {path}")
            except Exception:
                logging.exception('Error loading file')
                QMessageBox.critical(self, "Open Error", "Failed to load file. See logs.")

    def _save_file(self):
        logging.info("Save action triggered")
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Vispy Files (*.vp *.json);;All Files (*)")
        if path:
            try:
                import savesystem as ss
                ss.save_scene_to_file(self.scene, path)
                QMessageBox.information(self, "Save", f"Saved to: {path}")
            except Exception:
                logging.exception('Error saving file')
                QMessageBox.critical(self, "Save Error", "Failed to save file. See logs.")

    def _save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Vispy Files (*.vp *.json);;All Files (*)")
        if path:
            try:
                import savesystem as ss
                ss.save_scene_to_file(self.scene, path)
                logging.info(f"Save as: {path}")
                QMessageBox.information(self, "Save As", f"Saved to: {path}")
            except Exception:
                logging.exception('Error saving file as')
                QMessageBox.critical(self, "Save Error", "Failed to save file. See logs.")

    def _show_preferences(self):
        QMessageBox.information(self, "Preferences", "Preferences dialog - implement settings here")

    def _show_about(self):
        QMessageBox.information(self, "About", "Vispy Proof of Concept\nPlaceholder menus - implement functionality.")

app = QApplication(sys.argv)
window = NodeEditor()
window.show()
try:
    rc = app.exec()
except Exception:
    logging.exception('Unhandled exception in main loop')
    rc = 1
finally:
    try:
        # flush handlers
        logging.shutdown()
    except Exception:
        pass
sys.exit(rc)


#56+115+114 
