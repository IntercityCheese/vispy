from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QComboBox, QLineEdit, QApplication, QSizePolicy, QTreeWidget, QTreeWidgetItem, QStackedWidget
from PySide6.QtGui import (
    QPainter, QMouseEvent, QColor, QPen, QDrag, QCursor
)
from PySide6.QtCore import Qt, QEvent, QLineF, QMimeData, QPoint

import sys, traceback, logging, os

# basic file logging for debugging silent crashes
_log_path = os.path.join(os.path.dirname(__file__), 'vispy_debug.log')
logging.basicConfig(level=logging.DEBUG, filename=_log_path, filemode='a',
                    format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

def _exception_hook(exctype, value, tb):
    logging.error('Uncaught exception', exc_info=(exctype, value, tb))
    # still print to console for interactive runs
    print('Uncaught exception:', value)
    traceback.print_exception(exctype, value, tb)

sys.excepthook = _exception_hook

import types_classes.node_library as nl
from widgets_elements.vispyNodeLib import Node
from types_classes.vispyDataTypes import types


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
        # allow variable dragging from left panel
        self.setAcceptDrops(True)

        # Zoom configuration: min/max absolute scales and per-step multiplier
        # Can be adjusted externally if needed
        self._min_scale = 0.4
        self._max_scale = 2
        self._zoom_step = 1.25
        
        # Store last right-click position for node creation
        self._context_menu_pos = None

    def wheelEvent(self, event):
        """Zoom view under mouse, clamped between min and max scale.

        The wheel's angleDelta is divided by 120 to get standard notch steps
        (positive for zoom in, negative for zoom out). Supports multiple-step
        scrolls by raising the zoom step to the power of steps.
        """
        # number of standardized wheel steps (120 units per notch)
        steps = event.angleDelta().y() / 120.0
        if steps == 0:
            event.ignore()
            return

        # compute factor to apply (handles fractional or multiple steps)
        factor = self._zoom_step ** steps

        # current uniform scale (m11 == m22 for typical transforms)
        current = self.transform().m11()

        # clamp to min/max scale by adjusting the applied factor
        new_scale = current * factor
        if new_scale < self._min_scale:
            factor = self._min_scale / current
        elif new_scale > self._max_scale:
            factor = self._max_scale / current

        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = QMouseEvent(
                QEvent.MouseButtonPress,
                event.position(),
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier
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
                Qt.NoModifier
            )
            super().mouseReleaseEvent(fake)
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        md = event.mimeData()
        if md.hasFormat('application/x-variable'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        md = event.mimeData()
        if md.hasFormat('application/x-variable'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        md = event.mimeData()
        if not md.hasFormat('application/x-variable'):
            event.ignore()
            return
        data = bytes(md.data('application/x-variable')).decode()
        try:
            name, type_key = data.split('|', 1)
        except Exception:
            event.ignore()
            return

        pos = event.position().toPoint()
        scene_pos = self.mapToScene(pos)
        menu = QMenu(self)
        action_get = menu.addAction(f"Create Get '{name}'")
        action_set = menu.addAction(f"Create Set '{name}'")
        action = menu.exec(QCursor.pos())
        if action == action_get:
            node = Node(nl.make_get_variable_node())
            node.title = f"Get {name}"
            node.setPos(scene_pos)
            self.scene().addItem(node)
            event.acceptProposedAction()
        elif action == action_set:
            node = Node(nl.make_set_variable_node())
            node.title = f"Set {name}"
            node.setPos(scene_pos)
            self.scene().addItem(node)
            event.acceptProposedAction()
        else:
            event.ignore()
    
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

        # Zoom configuration: min/max absolute scales and per-step multiplier
        # Can be adjusted externally if needed
        self._min_scale = 0.4
        self._max_scale = 2
        self._zoom_step = 1.25
        
        # Store last right-click position for node creation
        self._context_menu_pos = None
        
        # Populate node creators dynamically
        self._populate_node_types()

    def contextMenuEvent(self, event):
        """Show context menu on right-click with dynamically generated node creation options."""
        self._context_menu_pos = self.mapToScene(event.pos())
        
        menu = QMenu(self)
        
        # Dynamically add node creation options
        for display_name, creator_func in self._node_creators.items():
            action = menu.addAction(display_name)
            action.triggered.connect(lambda checked, func=creator_func: self._create_node(func))
        
        menu.exec(event.globalPos())
    
    def _populate_node_types(self):
        """Dynamically generate node creation actions from node_library."""
        self._node_creators = {}
        
        # Find all make_*_node functions in nl module
        for attr_name in dir(nl):
            if attr_name.startswith('make_') and attr_name.endswith('_node'):
                func = getattr(nl, attr_name)
                if callable(func):
                    # Convert make_cast_to_string_node to "Cast To String Node"
                    node_type = attr_name[5:-5]  # Remove 'make_' and '_node'
                    display_name = ' '.join(word.capitalize() for word in node_type.split('_')) + ' Node'
                    self._node_creators[display_name] = func
    
    def _create_node(self, creator_func):
        """Create a node using the provided creator function."""
        if self._context_menu_pos is not None:
            node = Node(creator_func())
            node.setPos(self._context_menu_pos)
            self.scene().addItem(node)


class VariableItemWidget(QWidget):
    """Widget representing one variable in the manager list."""
    def __init__(self, name, type_key, type_names, manager=None):
        super().__init__(manager)
        self.manager = manager
        self.name = name
        self.type_key = type_key
        self._editing = False
        self._old_name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        # stacked widget to switch between label and edit (only one shown at a time)
        name_stack = QStackedWidget()
        
        # display label (mouse events pass through)
        self.label = QLabel(self.name)
        self.label.setToolTip(self.name)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # hidden edit field
        self.name_edit = QLineEdit(self.name)
        self.name_edit.setFrame(False)
        self.name_edit.editingFinished.connect(self._finish_edit_name)
        self.name_edit.returnPressed.connect(self._finish_edit_name)

        # keep stack reference on the widget so we can toggle reliably
        self.name_stack = name_stack
        self.name_stack.addWidget(self.label)  # index 0
        self.name_stack.addWidget(self.name_edit)  # index 1
        self.name_stack.setCurrentIndex(0)  # show label by default

        self.combo = QComboBox()
        self.combo.addItems(type_names)
        self.combo.setFixedWidth(110)
        if self.type_key in type_names:
            self.combo.setCurrentText(self.type_key)
        # use activated so only user actions trigger the handler
        self.combo.activated.connect(lambda idx: self._on_type_changed(self.combo.itemText(idx)))

        self.del_btn = QPushButton('\u00D7')
        self.del_btn.setFixedSize(20, 20)
        self.del_btn.clicked.connect(self._on_deleted)

        layout.addWidget(name_stack)
        layout.addStretch()
        layout.addWidget(self.combo)
        layout.addWidget(self.del_btn)

        self._press_pos = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_get = menu.addAction(f"Create Get '{self.name}'")
        action_set = menu.addAction(f"Create Set '{self.name}'")
        action = menu.exec(QCursor.pos())
        if action == action_get and self.manager:
            self.manager.create_variable_node(self.name, 'get')
        elif action == action_set and self.manager:
            self.manager.create_variable_node(self.name, 'set')
        else:
            super().contextMenuEvent(event)

    def _on_deleted(self):
        if self.manager:
            self.manager.remove_variable(self.name)

    def _on_type_changed(self, text):
        self.type_key = text
        logging.debug(f"Type change requested for variable '{self.name}' -> '{text}'")
        if self.manager:
            try:
                # prefer moving by widget reference to avoid searching
                if hasattr(self.manager, 'update_variable_type_widget'):
                    self.manager.update_variable_type_widget(self, text)
                else:
                    self.manager.update_variable_type(self.name, text)
            except Exception:
                logging.exception('Error updating variable type')
                # ensure no crash propagation
                try:
                    self.type_key = text
                except Exception:
                    pass

    def start_edit(self):
        """Enter edit mode for the name."""
        self._editing = True
        self.name_edit.setText(self.name)
        # switch to edit field in the stored stacked widget
        try:
            self.name_stack.setCurrentIndex(1)
        except Exception:
            for child in self.findChildren(QStackedWidget):
                child.setCurrentIndex(1)
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def _finish_edit_name(self):
        """Exit edit mode and save name if changed."""
        if not self._editing:
            return
        self._editing = False
        new_name = self.name_edit.text().strip()
        if not new_name:
            new_name = self._old_name
        if new_name != self._old_name and self.manager:
            self.manager.update_variable_name(self._old_name, new_name)
            self._old_name = new_name
        self.name = new_name
        self.label.setText(self.name)
        # switch back to label in the stored stacked widget
        try:
            self.name_stack.setCurrentIndex(0)
        except Exception:
            for child in self.findChildren(QStackedWidget):
                child.setCurrentIndex(0)

    def mouseDoubleClickEvent(self, event):
        """Enter edit mode on double-click."""
        if not self._editing:
            self.start_edit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self._editing:
            self._press_pos = event.pos()
            if self.manager:
                self.manager.select_variable_widget(self)
        event.ignore()  # let list handle selection

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._press_pos is not None and not self._editing:
            dist = (event.pos() - self._press_pos).manhattanLength()
            if dist >= QApplication.startDragDistance():
                drag = QDrag(self)
                md = QMimeData()
                md.setData('application/x-variable', f"{self.name}|{self.combo.currentText()}".encode())
                drag.setMimeData(md)
                drag.exec(Qt.CopyAction)
                self._press_pos = None
                return
        event.ignore()

    def focusOutEvent(self, event):
        if self._editing:
            self._finish_edit_name()
        super().focusOutEvent(event)


class VariableManagerWidget(QWidget):
    """Left-side variable manager panel with type-based grouping."""
    def __init__(self, parent=None, view=None):
        super().__init__(parent)
        self._view = view

        # mapping display name -> TypeProfile
        self._type_map = {
            types.string.name: types.string,
            types.float.name: types.float,
            types.integer.name: types.integer,
            types.boolean.name: types.boolean,
            types.exec.name: types.exec,
            types.any.name: types.any,
            types.text.name: types.text,
            types.eval.name: types.eval,
        }
        type_names = list(self._type_map.keys())
        self._type_names = type_names

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel("Variables")
        title.setStyleSheet('font-weight: bold;')
        layout.addWidget(title)

        # use tree widget instead of list for grouping by type
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Variables"])
        self.tree.setColumnCount(1)
        layout.addWidget(self.tree)

        # dict to track type group items: type_key -> QTreeWidgetItem
        self._type_groups = {}
        for type_key in type_names:
            group_item = QTreeWidgetItem([type_key])
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.tree.addTopLevelItem(group_item)
            self._type_groups[type_key] = group_item

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Variable")
        add_btn.clicked.connect(lambda: self.add_variable('new_var', types.string.name))
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        # placeholder variables
        self.add_variable('score', types.integer.name)
        self.add_variable('player_name', types.string.name)
        self.add_variable('alive', types.boolean.name)

        # stretch
        layout.addStretch()

        # allow resizing in splitter: set minimum width but not fixed
        self.setMinimumWidth(160)
        self.setMaximumWidth(600)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def add_variable(self, name, type_key):
        # create unique name if needed
        existing_names = self._get_all_variable_names()
        suffix = 1
        new_name = name
        while new_name in existing_names:
            new_name = f"{name}_{suffix}"
            suffix += 1

        # add to type group
        type_group = self._type_groups.get(type_key)
        if type_group is None:
            return

        item = QTreeWidgetItem()
        # hide the tree item's own text; widget handles display
        item.setText(0, "")
        item.setData(0, Qt.UserRole, new_name)
        w = VariableItemWidget(new_name, type_key, self._type_names, manager=self)
        # attach back-reference so widget knows its tree item
        w._tree_item = item
        item.setSizeHint(0, w.sizeHint())
        type_group.addChild(item)
        self.tree.setItemWidget(item, 0, w)
        # ensure the group is expanded so the widget is visible
        type_group.setExpanded(True)

    def _get_all_variable_names(self):
        """Get all variable names from tree."""
        names = []
        for type_key, group in self._type_groups.items():
            for i in range(group.childCount()):
                child = group.child(i)
                w = self.tree.itemWidget(child, 0)
                if w and hasattr(w, 'name'):
                    names.append(w.name)
        return names

    def select_variable_widget(self, widget):
        """Select the tree item for the given widget."""
        for type_key, group in self._type_groups.items():
            for i in range(group.childCount()):
                child = group.child(i)
                w = self.tree.itemWidget(child, 0)
                if w is widget:
                    self.tree.setCurrentItem(child)
                    return

    def update_variable_name(self, old_name, new_name):
        # ensure unique
        base = new_name
        existing = [n for n in self._get_all_variable_names() if n != old_name]
        suffix = 1
        unique = new_name
        while unique in existing:
            unique = f"{base}_{suffix}"
            suffix += 1
        
        for type_key, group in self._type_groups.items():
            for i in range(group.childCount()):
                child = group.child(i)
                w = self.tree.itemWidget(child, 0)
                if w and w.name == old_name:
                    w.name = unique
                    w._old_name = unique
                    w.label.setText(unique)
                    w.label.setToolTip(unique)
                    # store canonical name in item data for robustness
                    child.setData(0, Qt.UserRole, unique)
                    return

    def remove_variable(self, name):
        # remove first matching variable from tree
        for type_key, group in self._type_groups.items():
            for i in range(group.childCount()):
                child = group.child(i)
                w = self.tree.itemWidget(child, 0)
                if w and getattr(w, 'name', None) == name:
                    group.removeChild(child)
                    return

    def update_variable_type(self, name, type_key):
        """Move the variable's tree item to a different type group safely (fallback)."""
        # try to use widget backref if available
        for tkey, group in self._type_groups.items():
            for i in range(group.childCount()):
                child = group.child(i)
                w = self.tree.itemWidget(child, 0)
                if w and w.name == name:
                    try:
                        self.update_variable_type_widget(w, type_key)
                    except Exception as e:
                        print(f"Error in update_variable_type (fallback): {e}")
                    return


    def create_variable_node(self, name, op):
        """Create a get/set variable node at the center of the view."""
        if not getattr(self, '_view', None):
            return
        center = self._view.viewport().rect().center()
        scene_pos = self._view.mapToScene(center)
        if op == 'get':
            node = Node(nl.make_get_variable_node())
            node.title = f"Get {name}"
        else:
            node = Node(nl.make_set_variable_node())
            node.title = f"Set {name}"
        node.setPos(scene_pos)
        self._view.scene().addItem(node)

    def update_variable_type_widget(self, widget, type_key):
        """Move a variable widget's item to a different type group safely by recreating it."""
        logging.debug(f"Attempting to recreate widget '{getattr(widget,'name',None)}' to type '{type_key}'")
        try:
            child = getattr(widget, '_tree_item', None)
            old_group = None
            if child is None:
                # attempt to find the corresponding child
                for tkey, group in self._type_groups.items():
                    for i in range(group.childCount()):
                        c = group.child(i)
                        w = self.tree.itemWidget(c, 0)
                        if w is widget:
                            child = c
                            old_group = group
                            break
                    if child:
                        break
            else:
                old_group = child.parent()

            if child is None:
                logging.warning(f"Could not find tree item for widget '{widget.name}'")
                widget.type_key = type_key
                return

            # find new group
            if type_key not in self._type_groups:
                widget.type_key = type_key
                return
            new_group = self._type_groups[type_key]

            # if already in place, just update
            if old_group is new_group:
                widget.type_key = type_key
                logging.debug('Widget already in target group; type_key updated')
                return

            logging.debug('Recreating widget in new group')
            # create new item and widget in new group
            new_item = QTreeWidgetItem()
            new_item.setText(0, '')
            new_item.setData(0, Qt.UserRole, widget.name)
            new_widget = VariableItemWidget(widget.name, type_key, self._type_names, manager=self)
            new_widget._tree_item = new_item
            new_item.setSizeHint(0, new_widget.sizeHint())
            new_group.addChild(new_item)
            self.tree.setItemWidget(new_item, 0, new_widget)
            new_group.setExpanded(True)

            # remove old item and schedule old widget for deletion
            try:
                self.tree.removeItemWidget(child, 0)
            except Exception:
                logging.debug('removeItemWidget failed or not necessary')
            try:
                old_group.removeChild(child)
            except Exception:
                logging.debug('removeChild failed')
            try:
                widget.deleteLater()
            except Exception:
                logging.debug('deleteLater failed')

            logging.debug('Recreate move successful')
        except Exception:
            logging.exception('Error recreating widget')
            try:
                widget.type_key = type_key
            except Exception:
                pass
            try:
                widget.type_key = type_key
            except Exception:
                pass


class GraphicsScene(QGraphicsScene):

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        grid = 20

        left = int(rect.left()) - (int(rect.left()) % grid)
        top = int(rect.top()) - (int(rect.top()) % grid)

        lines = []

        for x in range(left, int(rect.right()), grid):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))

        for y in range(top, int(rect.bottom()), grid):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawLines(lines)
