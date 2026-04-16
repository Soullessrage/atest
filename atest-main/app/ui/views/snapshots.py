from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.application import ApplicationContext
from app.ui.viewmodels.snapshot_viewmodel import SnapshotViewModel


class SnapshotPage(QWidget):
    def __init__(self, view_model: SnapshotViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_snapshot_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Snapshots")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        self.world_selector = QComboBox()
        self.world_selector.addItems([world.name for world in self.view_model.available_worlds()])
        layout.addWidget(self.world_selector)

        self.snapshot_list = QListWidget()
        layout.addWidget(self.snapshot_list)

        button_row = QHBoxLayout()
        self.create_button = QPushButton("Create Snapshot")
        self.restore_button = QPushButton("Restore Selected")
        button_row.addWidget(self.create_button)
        button_row.addWidget(self.restore_button)
        layout.addLayout(button_row)

        self.create_button.clicked.connect(self.create_snapshot)
        self.restore_button.clicked.connect(self.restore_selected_snapshot)

    def refresh_snapshot_list(self) -> None:
        self.snapshot_list.clear()
        for snapshot in self.view_model.list_snapshots():
            created = snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
            self.snapshot_list.addItem(f"{snapshot.name} ({snapshot.id}) - {created}")

    def create_snapshot(self) -> None:
        current_world = self.world_selector.currentText()
        if not current_world:
            return
        selected = next((w for w in self.view_model.available_worlds() if w.name == current_world), None)
        if not selected:
            return
        self.view_model.create_snapshot(selected.id, f"Snapshot for {selected.name}")
        self.refresh_snapshot_list()

    def restore_selected_snapshot(self) -> None:
        current_item = self.snapshot_list.currentItem()
        if not current_item:
            return
        snapshot_id = current_item.text().split("(")[-1].split(")")[0]
        self.view_model.restore_snapshot(snapshot_id)
