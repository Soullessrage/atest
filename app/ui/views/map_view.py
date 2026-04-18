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
    QFrame,
)

from app.ui.viewmodels.map_viewmodel import MapViewModel


class MapViewPage(QWidget):
    def __init__(self, view_model: MapViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_world_selector()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f4e4bc, stop:1 #d4b08a);
                border: 2px solid #8b4513;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title = QLabel("Map")
        title.setStyleSheet("""
            QLabel {
                color: #5d4e37;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Explore the geography of your worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: #8b4513;
                font-size: 16px;
                font-family: 'Times New Roman', serif;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_frame)

        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #fefcf4;
                border: 2px solid #d4b08a;
                border-radius: 12px;
                padding: 20px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)

        world_label = QLabel("Select World:")
        world_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #5d4e37;
                font-family: 'Times New Roman', serif;
                margin-right: 10px;
            }
        """)
        controls_layout.addWidget(world_label)

        self.world_selector = QComboBox()
        self.world_selector.setStyleSheet("""
            QComboBox {
                border: 2px solid #d4b08a;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: #fefcf4;
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                min-width: 200px;
                color: #5d4e37;
            }
            QComboBox:hover {
                border-color: #8b4513;
                background-color: #f9f6f0;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #d4b08a;
                border-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #5d4e37;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #fefcf4;
                border: 1px solid #d4b08a;
                selection-background-color: #d4b08a;
                color: #5d4e37;
                font-family: 'Times New Roman', serif;
            }
        """)
        controls_layout.addWidget(self.world_selector)
        controls_layout.addStretch()

        self.refresh_button = QPushButton("Refresh Map")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #d4b08a;
                color: #5d4e37;
                border: 2px solid #8b4513;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
            }
            QPushButton:hover {
                background-color: #b8956a;
                border-color: #654321;
            }
            QPushButton:pressed {
                background-color: #a0784a;
            }
        """)
        controls_layout.addWidget(self.refresh_button)

        layout.addWidget(controls_frame)

        map_frame = QFrame()
        map_frame.setStyleSheet("""
            QFrame {
                background-color: #fefcf4;
                border: 2px solid #d4b08a;
                border-radius: 12px;
                padding: 5px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
        map_layout = QVBoxLayout(map_frame)

        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor("#fefcf4")))

        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("""
            QGraphicsView {
                border: none;
                border-radius: 8px;
                background-color: #fefcf4;
            }
        """)
        self.view.setRenderHint(self.view.renderHints())
        map_layout.addWidget(self.view)

        layout.addWidget(map_frame, 1)

        self.refresh_button.clicked.connect(self.refresh_map)

    def refresh_world_selector(self) -> None:
        selected_id = self.world_selector.currentData()
        self.world_selector.blockSignals(True)
        self.world_selector.clear()
        self.world_selector.addItem("Select a world...", None)
        for world in self.view_model.available_worlds():
            self.world_selector.addItem(world.name, world.id)
        self.world_selector.blockSignals(False)
        if selected_id is not None:
            index = self.world_selector.findData(selected_id)
            if index != -1:
                self.world_selector.setCurrentIndex(index)

    def refresh_map(self) -> None:
        self.refresh_world_selector()
        world_id = self.world_selector.currentData()
        if not world_id:
            return

        graph = self.view_model.build_graph(world_id)
        self.scene.clear()

        for edge in graph.edges.values():
            source = graph.nodes.get(edge.source)
            target = graph.nodes.get(edge.target)
            if not source or not target:
                continue
            line = QGraphicsLineItem(source.x, source.y, target.x, target.y)
            line.setPen(QPen(QColor("#8b4513"), 2))
            self.scene.addItem(line)

        for node in graph.nodes.values():
            circle = QGraphicsEllipseItem(node.x - node.size / 2, node.y - node.size / 2, node.size, node.size)
            circle.setBrush(QBrush(QColor("#8b4513")))
            circle.setPen(QPen(QColor("#5d4e37"), 2))
            self.scene.addItem(circle)
            label = QGraphicsTextItem(node.label)
            label.setPos(node.x + node.size / 2 + 4, node.y - node.size / 2)
            self.scene.addItem(label)
