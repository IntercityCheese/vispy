from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtGui import (
    QPainter, QMouseEvent, QColor, QPen
)
from PySide6.QtCore import Qt, QEvent, QLineF

import types_classes.node_library as nl
from widgets_elements.vispyNodeLib import Node


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
