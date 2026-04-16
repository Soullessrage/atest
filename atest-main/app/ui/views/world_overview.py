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
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel


class WorldOverviewPage(QWidget):
    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_world_list()

    def _build_ui(self) -> None:
        self.setWindowTitle("World Overview")
        layout = QVBoxLayout(self)

        header = QLabel("World Overview")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.world_list = QListWidget()
        layout.addWidget(self.world_list)

        button_row = QHBoxLayout()
        self.new_world_button = QPushButton("Create Sample World")
        self.export_button = QPushButton("Export Selected World")
        button_row.addWidget(self.new_world_button)
        button_row.addWidget(self.export_button)
        layout.addLayout(button_row)

        self.new_world_button.clicked.connect(self.create_sample_world)
        self.export_button.clicked.connect(self.export_selected_world)

    def refresh_world_list(self) -> None:
        self.world_list.clear()
        worlds = self.view_model.list_worlds()
        for world in worlds:
            self.world_list.addItem(f"{world.name} ({world.id})")

    def create_sample_world(self) -> None:
        world = self.view_model.create_world(
            name="New Campaign World",
            description="A fresh world generated for campaign building.",
        )
        self.world_list.addItem(f"{world.name} ({world.id})")

    def export_selected_world(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            return
        world_id = current_item.text().split("(")[-1].strip(")")
        world = next((w for w in self.view_model.list_worlds() if w.id == world_id), None)
        if not world:
            return
        target = Path.cwd() / f"world_export_{world.id}.json"
        self.view_model.export_world(world, target)
