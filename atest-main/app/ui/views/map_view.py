from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.viewmodels.map_viewmodel import MapViewModel


class MapViewPage(QWidget):
    def __init__(self, view_model: MapViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("World Map")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        controls = QHBoxLayout()
        self.world_selector = QComboBox()
        self.world_selector.addItems(self.view_model.available_worlds())
        self.refresh_button = QPushButton("Refresh Map")
        controls.addWidget(self.world_selector)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        layout.addWidget(self.view, 1)

        self.refresh_button.clicked.connect(self.refresh_map)

    def refresh_map(self) -> None:
        if self.world_selector.currentText() == "":
            return
        graph = self.view_model.build_graph(self.world_selector.currentText())
        self.scene.clear()
        for edge in graph.edges.values():
            source = graph.nodes.get(edge.source)
            target = graph.nodes.get(edge.target)
            if not source or not target:
                continue
            line = QGraphicsLineItem(source.x, source.y, target.x, target.y)
            line.setPen(QPen(QColor("#666666"), 2))
            self.scene.addItem(line)

        for node in graph.nodes.values():
            circle = QGraphicsEllipseItem(node.x - node.size / 2, node.y - node.size / 2, node.size, node.size)
            circle.setBrush(QBrush(QColor("#0077cc")))
            circle.setPen(QPen(QColor("#003a66"), 1))
            self.scene.addItem(circle)
            label = QGraphicsTextItem(node.label)
            label.setPos(node.x + node.size / 2 + 4, node.y - node.size / 2)
            self.scene.addItem(label)
