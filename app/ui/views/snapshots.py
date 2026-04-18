from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QComboBox,
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

from app.ui.viewmodels.snapshot_viewmodel import SnapshotViewModel


class SnapshotPage(QWidget):
    def __init__(self, view_model: SnapshotViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_world_selector()
        self.refresh_snapshot_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title = QLabel("📸 Snapshots")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Save and restore your world states")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_frame)

        selector_frame = QFrame()
        selector_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 20px;
            }
        """)
        selector_layout = QVBoxLayout(selector_frame)

        selector_title = QLabel("🌍 Select World for Snapshots")
        selector_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        selector_layout.addWidget(selector_title)

        self.world_selector = QComboBox()
        self.world_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 300px;
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
        selector_layout.addWidget(self.world_selector)
        layout.addWidget(selector_frame)

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

        list_title = QLabel("📋 Available Snapshots")
        list_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        list_layout.addWidget(list_title)

        self.snapshot_list = QListWidget()
        self.snapshot_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
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
        list_layout.addWidget(self.snapshot_list)
        layout.addWidget(list_frame)

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

        self.create_button = QPushButton("📸 Create Snapshot")
        self.create_button.setStyleSheet("""
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

        self.restore_button = QPushButton("🔄 Restore Selected")
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)

        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        button_layout.addWidget(self.restore_button)
        layout.addWidget(button_frame)

        self.create_button.clicked.connect(self.create_snapshot)
        self.restore_button.clicked.connect(self.restore_selected_snapshot)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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

    def refresh_snapshot_list(self) -> None:
        self.snapshot_list.clear()
        for snapshot in self.view_model.list_snapshots():
            created = snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
            self.snapshot_list.addItem(f"{snapshot.name} ({snapshot.id}) - {created}")

    def create_snapshot(self) -> None:
        self.refresh_world_selector()
        world_id = self.world_selector.currentData()
        if not world_id:
            return
        self.view_model.create_snapshot(world_id, f"Snapshot for {self.world_selector.currentText()}")
        self.refresh_snapshot_list()

    def restore_selected_snapshot(self) -> None:
        current_item = self.snapshot_list.currentItem()
        if not current_item:
            return
        snapshot_id = current_item.text().split("(")[-1].split(")")[0]
        self.view_model.restore_snapshot(snapshot_id)
