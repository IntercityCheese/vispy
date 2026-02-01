from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyle,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QLineEdit,
    QComboBox
)
from PySide6.QtGui import QPen, QColor, QPainterPath, QFont
from PySide6.QtCore import QRectF, Qt, QPointF

import types_classes.vispyDataTypes as vdt
import types_classes.node_library as nl

class Node(QGraphicsItem):
    def __init__(self, node_data):
        super().__init__()

        self.data = node_data
        self.title = node_data.node_type

        self.width = 160
        self.height = 80
        self.sockets = []

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        y_offset = 30
        spacing = 20

        # input sockets
        for i, (name, t) in enumerate(node_data.inputs.items()):
            sock = Socket(self, 0, y_offset + i * spacing, t, name)
            self.sockets.append(sock)

        # output sockets
        for i, (name, t) in enumerate(node_data.outputs.items()):
            sock = Socket(self, self.width, y_offset + i * spacing, t, name)
            self.sockets.append(sock)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):

        if option.state & QStyle.State_Selected:
            pen = QPen(QColor(0, 170, 255), 3)
        else:
            pen = QPen(Qt.black, 2)

        painter.setPen(pen)
        painter.setBrush(QColor(45, 45, 45))

        painter.drawRoundedRect(
            0, 0, self.width, self.height, 6, 6
        )

        painter.setPen(Qt.white)
        painter.drawText(10, 20, self.title)

    def itemChange(self, change, value):
        # Intercept the proposed position so we can snap it to the grid.
        if change == QGraphicsItem.ItemPositionChange:
            grid = 20
            # `value` is the proposed new position (QPointF)
            try:
                x = value.x()
                y = value.y()
                snapped = QPointF(round(x / grid) * grid, round(y / grid) * grid)
                return snapped
            except Exception:
                return value

        # After the position has changed, update connected edges' geometry.
        if change == QGraphicsItem.ItemPositionHasChanged:
            for socket in self.sockets:
                for edge in socket.edges:
                    edge.update_path()

        return super().itemChange(change, value)


class Socket(QGraphicsItem):
    def __init__(self, parent, x, y, type, name=""):
        super().__init__(parent)

        self.radius = 6
        self.edges = []

        self.setPos(x, y)
        # allow the socket to handle mouse interactions
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)

        # transient fields used during drag
        self._dragging = False
        self._drag_edge = None

        # store the socket data type and name on the instance
        self.type = type
        self.name = name
        
        # create input widget if needed (TextInput or EvalInput)
        self._text_input = None
        self._combo_box = None
        self._proxy = None
        if self.type.shape == "TextInput":
            self._setup_text_input()
        elif self.type.shape == "EvalInput":
            self._setup_eval_input()

    def _setup_text_input(self):
        """Create and set up the text input widget"""
        self._text_input = QLineEdit()
        self._text_input.setPlaceholderText(self.name)
        self._text_input.setFixedSize(60, 18)
        self._text_input.setStyleSheet(
            "QLineEdit { background-color: #3c3c3c; color: white; border: 1px solid white; padding: 2px; margin: 0px; }"
        )
        
        # Create proxy widget to embed QLineEdit in the graphics scene
        self._proxy = QGraphicsProxyWidget(self)
        self._proxy.setWidget(self._text_input)
        # Position the proxy to the right of the socket, inside the node
        self._proxy.setPos(8, -9)

    def _setup_eval_input(self):
        """Create and set up the evaluation dropdown widget"""
        self._combo_box = QComboBox()
        self._combo_box.addItems(["==", ">=", "<=", "!="])
        self._combo_box.setFixedSize(55, 18)
        self._combo_box.setStyleSheet(
            "QComboBox { background-color: #3c3c3c; color: white; border: 1px solid white; padding: 2px; margin: 0px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background-color: #3c3c3c; color: white; selection-background-color: #0066cc; }"
        )
        
        # Create proxy widget to embed QComboBox in the graphics scene
        self._proxy = QGraphicsProxyWidget(self)
        self._proxy.setWidget(self._combo_box)
        # Position the proxy to the right of the socket, inside the node
        self._proxy.setPos(8, -9)

    def boundingRect(self):
        if self.type.shape == "TextInput" or self.type.shape == "EvalInput":
            # Return bounding rect for input widgets
            return QRectF(8, -9, 60, 18)
        else:
            return QRectF(
                -self.radius,
                -self.radius,
                self.radius * 2,
                self.radius * 2
            )

    def paint(self, painter, option, widget=None):
        if self.type.shape == "TextInput" or self.type.shape == "EvalInput":
            # Don't paint anything here; the widgets are handled by proxy
            return
        
        painter.setBrush(QColor(self.type.color))
        painter.setPen(Qt.NoPen)
        
        if self.type.shape == "Rect":
            painter.drawRect(self.boundingRect())
        else:
            painter.drawEllipse(self.boundingRect())

        # draw the socket label next to the socket
        if getattr(self, 'name', ''):
            painter.setPen(Qt.white)
            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(self.name)
            if self.pos().x() <= 0:
                # input socket: label to the right
                rect = QRectF(self.radius + 6, -self.radius, text_w, self.radius * 2)
                painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, self.name)
            else:
                # output socket: label to the left (inside node)
                rect = QRectF(-text_w - self.radius - 6, -self.radius, text_w, self.radius * 2)
                painter.drawText(rect, Qt.AlignVCenter | Qt.AlignRight, self.name)

    def get_text_value(self):
        """Get the value from the text input if it exists"""
        if self._text_input is not None:
            return self._text_input.text()
        return None

    def set_text_value(self, value):
        """Set the value of the text input if it exists"""
        if self._text_input is not None:
            self._text_input.setText(str(value))

    def get_eval_value(self):
        """Get the selected value from the eval dropdown if it exists"""
        if self._combo_box is not None:
            return self._combo_box.currentText()
        return None

    def set_eval_value(self, value):
        """Set the value of the eval dropdown if it exists"""
        if self._combo_box is not None:
            index = self._combo_box.findText(str(value))
            if index >= 0:
                self._combo_box.setCurrentIndex(index)

    def mousePressEvent(self, event):
        # start a drag to create a temporary edge
        if event.button() == Qt.LeftButton:
            self._dragging = True
            scene = self.scene()
            # create an edge with current mouse position as the end
            self._drag_edge = Edge(self, event.scenePos(), self.type)
            scene.addItem(self._drag_edge)
            # register edge with self (only once)
            if self._drag_edge not in self.edges:
                self.edges.append(self._drag_edge)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_edge is not None:
            # update temporary edge to follow cursor
            self._drag_edge.set_end_point(event.scenePos())
            self._drag_edge.update_path()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging and self._drag_edge is not None:
            scene = self.scene()
            # find a socket under the release position (excluding self)
            items = scene.items(event.scenePos())
            target = None
            for it in items:
                if isinstance(it, Socket) and it is not self:
                    target = it
                    break

            if target is not None:
                # complete the connection
                self._drag_edge.set_end_socket(target)
                if self._drag_edge not in target.edges:
                    target.edges.append(self._drag_edge)
                # ensure path is updated
                self._drag_edge.update_path()
            else:
                # not connected -> remove temporary edge
                try:
                    scene.removeItem(self._drag_edge)
                except Exception:
                    pass
                try:
                    self.edges.remove(self._drag_edge)
                except ValueError:
                    pass

            self._drag_edge = None
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class Edge(QGraphicsPathItem):
    def __init__(self, start, end, type):
        super().__init__()

        # start is expected to be a Socket
        # end can be either a Socket or a QPointF (temporary)
        self.start = start
        self.end = end
        self._end_point = None
        
        self.type = type

        # if end is a point (QPointF), store it separately
        if hasattr(end, 'x') and hasattr(end, 'y') and not hasattr(end, 'scenePos'):
            self._end_point = end
        else:
            # if a Socket, ensure this edge is registered on it
            if hasattr(end, 'edges') and self not in end.edges:
                end.edges.append(self)

        # register on start socket if needed
        if hasattr(start, 'edges') and self not in start.edges:
            start.edges.append(self)

        self.setPen(QPen(QColor(self.type.color), 2.5))
        self.setZValue(-1)
        # ensure edge receives mouse events so it can be deleted
        self.setAcceptedMouseButtons(Qt.LeftButton)

        self.update_path()

    def set_end_point(self, point):
        self._end_point = point
        self.end = point

    def set_end_socket(self, socket):
        # connect to a socket
        self.end = socket
        self._end_point = None

    def update_path(self):
        path = QPainterPath()

        p1 = self.start.scenePos()

        if isinstance(self.end, QGraphicsItem):
            p2 = self.end.scenePos()
        else:
            # assume QPointF
            p2 = self._end_point

        if p2 is None:
            return

        path.moveTo(p1)

        dx = (p2.x() - p1.x()) * 0.5

        path.cubicTo(
            p1.x() + dx, p1.y(),
            p2.x() - dx, p2.y(),
            p2.x(), p2.y()
        )

        self.setPath(path)

    def mousePressEvent(self, event):
        # Alt+LeftClick deletes the edge
        if event.button() == Qt.LeftButton and (event.modifiers() & Qt.AltModifier):
            scene = self.scene()
            # remove from connected sockets lists
            if hasattr(self.start, 'edges') and self in self.start.edges:
                try:
                    self.start.edges.remove(self)
                except ValueError:
                    pass
            if isinstance(self.end, QGraphicsItem) and hasattr(self.end, 'edges') and self in self.end.edges:
                try:
                    self.end.edges.remove(self)
                except ValueError:
                    pass
            try:
                scene.removeItem(self)
            except Exception:
                pass
            event.accept()
        else:
            super().mousePressEvent(event)
