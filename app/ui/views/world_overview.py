"""World Overview page for world management and inspection."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel


class CreateWorldDialog(QDialog):
    """Dialog for creating a new world."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New World")
        self.setModal(True)
        self.setFixedSize(500, 360)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("🌍 Create New World")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #3d2b1f; font-family: 'Times New Roman', serif;"
        )
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter world name")
        self.name_input.setStyleSheet(
            "QLineEdit { border: 1px solid #b08b5b; border-radius: 6px; padding: 8px; background: white; }"
        )
        form.addRow("Name:", self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Brief world description")
        self.desc_input.setFixedHeight(90)
        self.desc_input.setStyleSheet(
            "QTextEdit { border: 1px solid #b08b5b; border-radius: 6px; padding: 8px; background: white; }"
        )
        form.addRow("Description:", self.desc_input)

        self.template_combo = QComboBox()
        self.template_combo.addItem("Empty world", "empty")
        self.template_combo.addItem("Sample world", "sample")
        self.template_combo.setStyleSheet(
            "QComboBox { border: 1px solid #b08b5b; border-radius: 6px; padding: 8px; background: white; }"
        )
        form.addRow("Template:", self.template_combo)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(
            "QPushButton { padding: 10px 18px; border-radius: 8px; background: #d3a97f; color: #3d2b1f; }"
        )
        button_row.addWidget(cancel_button)

        create_button = QPushButton("Create")
        create_button.clicked.connect(self.accept)
        create_button.setStyleSheet(
            "QPushButton { padding: 10px 18px; border-radius: 8px; background: #7aa56a; color: white; }"
        )
        button_row.addWidget(create_button)

        layout.addLayout(button_row)

    def get_data(self) -> Dict[str, str]:
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "template": self.template_combo.currentData(),
        }


class WorldOverviewPage(QWidget):
    """World Overview page for browsing and managing worlds."""

    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self.world_items: List[QListWidgetItem] = []
        self._setup_ui()
        self.refresh_world_list()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(22, 22, 22, 22)

        header = QLabel("🌍 World Library")
        header.setStyleSheet(
            "font-size: 30px; font-weight: bold; color: #3d2b1f; font-family: 'Times New Roman', serif;"
        )
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search worlds by name or description...")
        self.search_input.textChanged.connect(self._filter_world_list)
        self.search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #b08b5b; border-radius: 8px; padding: 10px; background: white; }"
        )
        toolbar.addWidget(self.search_input, 2)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Name (A-Z)", "name")
        self.sort_combo.addItem("Recent", "created")
        self.sort_combo.addItem("Largest", "population")
        self.sort_combo.setStyleSheet(
            "QComboBox { border: 1px solid #b08b5b; border-radius: 8px; padding: 10px; background: white; }"
        )
        self.sort_combo.currentIndexChanged.connect(self._sort_world_list)
        toolbar.addWidget(self.sort_combo, 1)

        layout.addLayout(toolbar)

        body = QHBoxLayout()
        body.setSpacing(16)

        left_panel = QFrame()
        left_panel.setStyleSheet(
            "QFrame { background: rgba(255, 250, 240, 0.95); border: 1px solid #c7b09d; border-radius: 12px; }"
        )
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        world_list_label = QLabel("Available Worlds")
        world_list_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4d3a26;")
        left_layout.addWidget(world_list_label)

        self.world_list = QListWidget()
        self.world_list.itemSelectionChanged.connect(self.on_world_selected)
        self.world_list.setStyleSheet(
            "QListWidget { border: 1px solid #c7b09d; border-radius: 8px; background: white; padding: 4px; }"
            "QListWidget::item { padding: 10px; margin: 2px 0; }"
            "QListWidget::item:selected { background: #d4b77a; color: #3d2b1f; }"
        )
        left_layout.addWidget(self.world_list, 1)

        left_buttons = QHBoxLayout()
        create_button = QPushButton("Create World")
        create_button.clicked.connect(self._show_create_world_dialog)
        create_button.setStyleSheet(
            "QPushButton { padding: 10px 14px; border-radius: 8px; background: #7aa56a; color: white; }"
        )
        left_buttons.addWidget(create_button)

        sample_button = QPushButton("Create Sample")
        sample_button.clicked.connect(self.create_sample_world)
        sample_button.setStyleSheet(
            "QPushButton { padding: 10px 14px; border-radius: 8px; background: #8b76b8; color: white; }"
        )
        left_buttons.addWidget(sample_button)

        left_layout.addLayout(left_buttons)

        body.addWidget(left_panel, 1)

        right_panel = QFrame()
        right_panel.setStyleSheet(
            "QFrame { background: rgba(255, 250, 240, 0.95); border: 1px solid #c7b09d; border-radius: 12px; }"
        )
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(14)

        info_header = QLabel("World Details")
        info_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #4d3a26;")
        right_layout.addWidget(info_header)

        self.info_label = QLabel("Select a world to see details and hierarchy.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            "QLabel { background: #faf1e6; border: 1px solid #e1c9b3; border-radius: 8px; padding: 12px; }"
        )
        right_layout.addWidget(self.info_label)

        self.count_label = QLabel("")
        self.count_label.setWordWrap(True)
        self.count_label.setStyleSheet(
            "QLabel { background: #faf1e6; border: 1px solid #e1c9b3; border-radius: 8px; padding: 12px; }"
        )
        right_layout.addWidget(self.count_label)

        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabels(["Type", "Name"])
        self.hierarchy_tree.setStyleSheet(
            "QTreeWidget { border: 1px solid #c7b09d; border-radius: 8px; background: white; }"
            "QTreeWidget::item { padding: 6px; }"
            "QTreeWidget::item:selected { background: #d4b77a; color: #3d2b1f; }"
        )
        right_layout.addWidget(self.hierarchy_tree, 1)

        export_button = QPushButton("Export Selected World")
        export_button.clicked.connect(self.export_selected_world)
        export_button.setStyleSheet(
            "QPushButton { padding: 12px 16px; border-radius: 8px; background: #d4a65f; color: #3d2b1f; }"
        )
        right_layout.addWidget(export_button)

        body.addWidget(right_panel, 2)

        layout.addLayout(body)

        footer = QHBoxLayout()
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #4d3a26; font-size: 14px;")
        footer.addWidget(self.stats_label)
        footer.addStretch()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_world_list)
        refresh_button.setStyleSheet(
            "QPushButton { padding: 10px 14px; border-radius: 8px; background: #8fb8d4; color: white; }"
        )
        footer.addWidget(refresh_button)

        layout.addLayout(footer)

    def refresh_world_list(self) -> None:
        self.world_list.clear()
        self.world_items.clear()

        worlds_data = self.view_model.list_worlds_with_counts()
        if not worlds_data:
            no_world = QListWidgetItem("No worlds created yet. Use Create World to begin.")
            no_world.setFlags(Qt.NoItemFlags)
            self.world_list.addItem(no_world)
            self._show_world_info(None)
            self._update_stats(0, 0, 0)
            return

        for data in sorted(worlds_data, key=lambda item: item["world"].name.lower()):
            world = data["world"]
            item = QListWidgetItem(f"{world.name} — {data['settlement_count']} settlements, {data['empire_count']} empires")
            item.setData(Qt.UserRole, world.id)
            self.world_list.addItem(item)
            self.world_items.append(item)

        self.world_list.setCurrentRow(0)
        self._sort_world_list()
        self._update_stats(
            len(worlds_data),
            sum(item["settlement_count"] for item in worlds_data),
            sum(item["empire_count"] for item in worlds_data),
        )

    def _filter_world_list(self, text: str) -> None:
        text = text.strip().lower()
        for item in self.world_items:
            world_id = item.data(Qt.UserRole)
            world = self.view_model.get_world_by_id(world_id)
            if not world:
                item.setHidden(True)
                continue
            visible = not text or text in world.name.lower() or text in (world.description or "").lower()
            item.setHidden(not visible)

    def _sort_world_list(self) -> None:
        sort_key = self.sort_combo.currentData()
        items = [item for item in self.world_items if not item.isHidden()]

        def key_func(item: QListWidgetItem):
            world_id = item.data(Qt.UserRole)
            world = self.view_model.get_world_by_id(world_id)
            if not world:
                return ""
            if sort_key == "created":
                return getattr(world, "created_at", "") or ""
            if sort_key == "population":
                return len(self.view_model.persistence_service.list_settlements(world.id))
            return world.name.lower()

        reverse = sort_key in {"created", "population"}
        for i, item in enumerate(sorted(items, key=key_func, reverse=reverse)):
            self.world_list.takeItem(self.world_list.row(item))
            self.world_list.insertItem(i, item)

    def on_world_selected(self) -> None:
        item = self.world_list.currentItem()
        if not item:
            self._show_world_info(None)
            return

        world_id = item.data(Qt.UserRole)
        if not world_id:
            self._show_world_info(None)
            return

        details = self.view_model.load_world_details(world_id)
        self._show_world_info(details)

    def _show_world_info(self, details: Optional[Dict[str, object]]) -> None:
        if not details or details.get("world") is None:
            self.info_label.setText("Select a world to see details and hierarchy.")
            self.count_label.setText("")
            self.hierarchy_tree.clear()
            return

        world = details["world"]
        continents = details["continents"]
        empires = details["empires"]
        kingdoms = details["kingdoms"]
        regions = details["regions"]
        settlements = details["settlements"]

        self.info_label.setText(
            f"<b>{world.name}</b><br>{world.description or 'No description provided.'}<br><br>"
            f"ID: {world.id}<br>Created: {getattr(world, 'created_at', 'Unknown')}"
        )
        self.count_label.setText(
            f"Continents: {len(continents)} | Empires: {len(empires)} | "
            f"Kingdoms: {len(kingdoms)} | Regions: {len(regions)} | Settlements: {len(settlements)}"
        )
        self._render_hierarchy_tree(world.name, continents, empires, kingdoms, regions, settlements)

    def _render_hierarchy_tree(
        self,
        world_name: str,
        continents: List,
        empires: List,
        kingdoms: List,
        regions: List,
        settlements: List,
    ) -> None:
        self.hierarchy_tree.clear()

        world_item = QTreeWidgetItem(["World", world_name])
        self.hierarchy_tree.addTopLevelItem(world_item)

        continent_items = {}
        for continent in continents:
            node = QTreeWidgetItem(["Continent", continent.name])
            world_item.addChild(node)
            continent_items[continent.id] = node

        empire_items = {}
        for empire in empires:
            parent = continent_items.get(empire.continent_id, world_item)
            node = QTreeWidgetItem(["Empire", empire.name])
            parent.addChild(node)
            empire_items[empire.id] = node

        kingdom_items = {}
        for kingdom in kingdoms:
            parent = empire_items.get(kingdom.empire_id) or continent_items.get(kingdom.continent_id, world_item)
            node = QTreeWidgetItem(["Kingdom", kingdom.name])
            parent.addChild(node)
            kingdom_items[kingdom.id] = node

        region_items = {}
        for region in regions:
            parent = (
                kingdom_items.get(region.kingdom_id)
                or empire_items.get(region.empire_id)
                or continent_items.get(region.continent_id)
                or world_item
            )
            node = QTreeWidgetItem(["Region", region.name])
            parent.addChild(node)
            region_items[region.id] = node

        for settlement in settlements:
            parent = (
                region_items.get(settlement.region_id)
                or kingdom_items.get(settlement.kingdom_id)
                or empire_items.get(settlement.empire_id)
                or continent_items.get(settlement.continent_id)
                or world_item
            )
            node = QTreeWidgetItem(["Settlement", settlement.name])
            parent.addChild(node)

        self.hierarchy_tree.expandAll()

    def _show_create_world_dialog(self) -> None:
        dialog = CreateWorldDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        data = dialog.get_data()
        if not data["name"]:
            QMessageBox.warning(self, "Invalid Input", "World name is required.")
            return

        try:
            if data["template"] == "sample":
                self.view_model.create_sample_world(data["name"], data["description"])
            else:
                self.view_model.create_world(data["name"], data["description"])
            self.refresh_world_list()
        except Exception as exc:
            QMessageBox.critical(self, "Create Failed", f"Unable to create world: {exc}")

    def create_sample_world(self) -> None:
        try:
            self.view_model.create_sample_world(
                name="Sample Campaign World",
                description="A starter world with sample content.",
            )
            self.refresh_world_list()
        except Exception as exc:
            QMessageBox.critical(self, "Create Failed", f"Unable to create sample world: {exc}")

    def export_selected_world(self) -> None:
        item = self.world_list.currentItem()
        if not item:
            return

        world_id = item.data(Qt.UserRole)
        if not world_id:
            return

        world = self.view_model.get_world_by_id(world_id)
        if not world:
            return

        target = Path.cwd() / f"world_export_{world.name.replace(' ', '_')}_{world.id}.json"
        try:
            self.view_model.export_full_world(world, target)
            QMessageBox.information(self, "Export Complete", f"Exported '{world.name}' to:\n{target}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", f"Unable to export world: {exc}")

    def _update_stats(self, world_count: int, settlement_count: int, empire_count: int) -> None:
        self.stats_label.setText(
            f"{world_count} worlds • {settlement_count} settlements • {empire_count} empires"
        )
