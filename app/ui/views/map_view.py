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
    QSpacerItem,
    QSizePolicy,
)

from app.ui.viewmodels.map_viewmodel import MapViewModel


class MapViewPage(QWidget):
    def __init__(self, view_model: MapViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🗺️ World Map")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Explore the geography of your worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)

        # Controls section
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 20px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        
        world_label = QLabel("🌍 Select World:")
        world_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-right: 10px;
            }
        """)
        controls_layout.addWidget(world_label)

        self.world_selector = QComboBox()
        self.world_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
                margin-right: 8px;
            }
        """)
        self.world_selector.addItems(self.view_model.available_worlds())
        controls_layout.addWidget(self.world_selector)
        
        controls_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh Map")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        controls_layout.addWidget(self.refresh_button)
        
        layout.addWidget(controls_frame)

        # Map view section
        map_frame = QFrame()
        map_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 5px;
            }
        """)
        map_layout = QVBoxLayout(map_frame)
        
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor("#f8f9fa")))
        
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("""
            QGraphicsView {
                border: none;
                border-radius: 8px;
            }
        """)
        self.view.setRenderHint(self.view.renderHints())
        map_layout.addWidget(self.view)
        
        layout.addWidget(map_frame, 1)

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
