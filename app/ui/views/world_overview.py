from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel


class WorldOverviewPage(QWidget):
    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_world_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🌍 World Overview")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Manage and explore your fantasy worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)

        # World list section
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 20px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        
        list_title = QLabel("📋 Your Worlds")
        list_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        list_layout.addWidget(list_title)

        self.world_list = QListWidget()
        self.world_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
                background-color: white;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        list_layout.addWidget(self.world_list)

        layout.addWidget(list_frame)

        # Button section
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 20px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        self.new_world_button = QPushButton("✨ Create Sample World")
        self.new_world_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        self.export_button = QPushButton("📤 Export Selected World")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
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
        
        button_layout.addWidget(self.new_world_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        
        layout.addWidget(button_frame)

        self.new_world_button.clicked.connect(self.create_sample_world)
        self.export_button.clicked.connect(self.export_selected_world)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def refresh_world_list(self) -> None:
        self.world_list.clear()
        worlds = self.view_model.list_worlds()
        if not worlds:
            self.world_list.addItem("No worlds created yet. Click 'Create Sample World' to get started! 🌟")
        else:
            for world in worlds:
                settlement_count = len(world.settlements)
                kingdom_count = len(world.kingdoms)
                empire_count = len(world.empires)
                
                display_text = f"🏰 {world.name}\n"
                display_text += f"   Settlements: {settlement_count} | Kingdoms: {kingdom_count} | Empires: {empire_count}\n"
                display_text += f"   ID: {world.id}"
                
                self.world_list.addItem(display_text)

    def create_sample_world(self) -> None:
        world = self.view_model.create_world(
            name="New Campaign World",
            description="A fresh world generated for campaign building.",
        )
        self.refresh_world_list()  # Refresh the entire list instead of manually adding

    def export_selected_world(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            return
        
        # Extract world ID from the display text (it's on the last line)
        text_lines = current_item.text().split('\n')
        if len(text_lines) < 3:
            return
        world_id_line = text_lines[2]  # "   ID: {world.id}"
        if not world_id_line.startswith("   ID: "):
            return
        world_id = world_id_line.replace("   ID: ", "")
        
        world = next((w for w in self.view_model.list_worlds() if w.id == world_id), None)
        if not world:
            return
        target = Path.cwd() / f"world_export_{world.id}.json"
        self.view_model.export_world(world, target)
        # Could add a success message here, but for now just export silently
