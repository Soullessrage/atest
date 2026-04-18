from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
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

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #daa520 0%, #cd853f 50%, #a0522d 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 
                    0 0 20px rgba(139, 69, 19, 0.6),
                    inset 0 0 15px rgba(0, 0, 0, 0.2);
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title = QLabel("🌍 World Overview")
        title.setStyleSheet("""
            QLabel {
                color: #f4e4bc;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                margin: 0;
            }
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Manage and explore your fantasy worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(244, 228, 188, 0.9);
                font-size: 18px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_frame)

        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(160, 82, 45, 0.06) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
        """)
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)

        self.world_list = QListWidget()
        self.world_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #daa520;
                border-radius: 12px;
                padding: 10px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
                box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.1);
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(218, 165, 32, 0.3);
                background-color: rgba(222, 184, 135, 0.3);
                border-radius: 6px;
                margin: 2px;
                color: #654321;
            }
            QListWidget::item:selected {
                background-color: rgba(205, 133, 63, 0.8);
                color: #f4e4bc;
                border: 2px solid #daa520;
                box-shadow: 0 0 8px rgba(218, 165, 32, 0.6);
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        content_layout.addWidget(self.world_list, 1)

        self.detail_panel = QFrame()
        self.detail_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #dfe6e9;
                padding: 20px;
            }
        """)
        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setSpacing(12)

        self.detail_title = QLabel("World Hierarchy Details")
        self.detail_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        detail_layout.addWidget(self.detail_title)

        self.detail_summary = QLabel("Select a world to inspect its continents, empires, kingdoms, regions, and settlements.")
        self.detail_summary.setWordWrap(True)
        self.detail_summary.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
            }
        """)
        detail_layout.addWidget(self.detail_summary)

        self.detail_counts = QLabel("")
        self.detail_counts.setWordWrap(True)
        self.detail_counts.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        detail_layout.addWidget(self.detail_counts)

        self.detail_entities = QLabel("")
        self.detail_entities.setWordWrap(True)
        self.detail_entities.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 13px;
            }
        """)
        detail_layout.addWidget(self.detail_entities)

        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabels(["Type", "Name"])
        self.hierarchy_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.hierarchy_tree.setRootIsDecorated(True)
        self.hierarchy_tree.setIndentation(18)
        detail_layout.addWidget(self.hierarchy_tree, 1)

        detail_layout.addStretch()
        content_layout.addWidget(self.detail_panel, 2)

        layout.addWidget(content_frame)

        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.9);
                background-image: 
                    radial-gradient(circle at 40% 60%, rgba(139, 69, 19, 0.08) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 12px rgba(139, 69, 19, 0.2),
                    inset 0 0 8px rgba(0, 0, 0, 0.05);
            }
        """)
        button_layout = QHBoxLayout(button_frame)

        self.new_world_button = QPushButton("✨ Create Sample World")
        self.new_world_button.setStyleSheet("""
            QPushButton {
                background-color: #228b22;
                background-image: linear-gradient(180deg, #32cd32 0%, #228b22 100%);
                color: #f4e4bc;
                border: 2px solid #006400;
                border-radius: 12px;
                padding: 14px 26px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 10px rgba(34, 139, 34, 0.4);
            }
            QPushButton:hover {
                background-color: #32cd32;
                background-image: linear-gradient(180deg, #32cd32 0%, #006400 100%);
                border-color: #228b22;
                box-shadow: 0 0 15px rgba(34, 139, 34, 0.6);
            }
            QPushButton:pressed {
                background-color: #006400;
                transform: translateY(1px);
                box-shadow: 0 0 5px rgba(34, 139, 34, 0.8);
            }
        """)

        self.export_button = QPushButton("📤 Export Selected World")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #daa520;
                background-image: linear-gradient(180deg, #daa520 0%, #cd853f 100%);
                color: #654321;
                border: 2px solid #a0522d;
                border-radius: 12px;
                padding: 14px 26px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 10px rgba(139, 69, 19, 0.4);
            }
            QPushButton:hover {
                background-color: #cd853f;
                background-image: linear-gradient(180deg, #cd853f 0%, #a0522d 100%);
                border-color: #8b4513;
                box-shadow: 0 0 15px rgba(139, 69, 19, 0.6);
            }
            QPushButton:pressed {
                background-color: #a0522d;
                transform: translateY(1px);
                box-shadow: 0 0 5px rgba(139, 69, 19, 0.8);
            }
        """)

        button_layout.addWidget(self.new_world_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)

        layout.addWidget(button_frame)

        self.world_list.currentItemChanged.connect(self.on_world_selected)
        self.new_world_button.clicked.connect(self.create_sample_world)
        self.export_button.clicked.connect(self.export_selected_world)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def refresh_world_list(self) -> None:
        self.world_list.clear()
        worlds_data = self.view_model.list_worlds_with_counts()
        if not worlds_data:
            self.world_list.addItem("No worlds created yet. Click 'Create Sample World' to get started! 🌟")
            self.render_world_details(None)
            return

        for data in worlds_data:
            world = data["world"]
            settlement_count = data["settlement_count"]
            kingdom_count = data["kingdom_count"]
            empire_count = data["empire_count"]
            display_text = f"🏰 {world.name}\n"
            display_text += f"   Settlements: {settlement_count} | Kingdoms: {kingdom_count} | Empires: {empire_count}\n"
            display_text += f"   ID: {world.id}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, world.id)
            self.world_list.addItem(item)

        self.world_list.setCurrentRow(0)

    def on_world_selected(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            self.render_world_details(None)
            return

        world_id = current_item.data(Qt.UserRole)
        if not world_id:
            self.render_world_details(None)
            return

        details = self.view_model.load_world_details(world_id)
        self.render_world_details(details)

    def render_world_details(self, details: dict | None) -> None:
        if details is None or details.get("world") is None:
            self.detail_summary.setText("Select a world to inspect its continents, empires, kingdoms, regions, and settlements.")
            self.detail_counts.setText("")
            self.detail_entities.setText("")
            self.hierarchy_tree.clear()
            return

        world = details["world"]
        continents = details["continents"]
        empires = details["empires"]
        kingdoms = details["kingdoms"]
        regions = details["regions"]
        settlements = details["settlements"]

        self.detail_summary.setText(f"<b>{world.name}</b> — {world.description or 'A detailed campaign world.'}")
        self.detail_counts.setText(
            f"Continents: {len(continents)} | Empires: {len(empires)} | Kingdoms: {len(kingdoms)} | Regions: {len(regions)} | Settlements: {len(settlements)}"
        )

        entity_lines = []
        if continents:
            entity_lines.append("Continents: " + ", ".join(continent.name for continent in continents))
        if empires:
            entity_lines.append("Empires: " + ", ".join(empire.name for empire in empires))
        if kingdoms:
            entity_lines.append("Kingdoms: " + ", ".join(kingdom.name for kingdom in kingdoms))
        if regions:
            entity_lines.append("Regions: " + ", ".join(region.name for region in regions))
        if settlements:
            entity_lines.append("Settlements: " + ", ".join(settlement.name for settlement in settlements))

        self.detail_entities.setText("\n".join(entity_lines))
        self.render_hierarchy_tree(world.name, continents, empires, kingdoms, regions, settlements)

    def render_hierarchy_tree(
        self,
        world_name: str,
        continents: list,
        empires: list,
        kingdoms: list,
        regions: list,
        settlements: list,
    ) -> None:
        self.hierarchy_tree.clear()

        world_item = QTreeWidgetItem(["World", world_name])
        self.hierarchy_tree.addTopLevelItem(world_item)

        continent_items = {}
        for continent in continents:
            continent_item = QTreeWidgetItem(["Continent", continent.name])
            world_item.addChild(continent_item)
            continent_items[continent.id] = continent_item

        empire_items = {}
        for empire in empires:
            parent = continent_items.get(empire.continent_id, world_item)
            empire_item = QTreeWidgetItem(["Empire", empire.name])
            parent.addChild(empire_item)
            empire_items[empire.id] = empire_item

        kingdom_items = {}
        for kingdom in kingdoms:
            parent = empire_items.get(kingdom.empire_id) or continent_items.get(kingdom.continent_id, world_item)
            kingdom_item = QTreeWidgetItem(["Kingdom", kingdom.name])
            parent.addChild(kingdom_item)
            kingdom_items[kingdom.id] = kingdom_item

        region_items = {}
        for region in regions:
            parent = kingdom_items.get(region.kingdom_id) or empire_items.get(region.empire_id) or continent_items.get(region.continent_id, world_item)
            region_item = QTreeWidgetItem(["Region", region.name])
            parent.addChild(region_item)
            region_items[region.id] = region_item

        for settlement in settlements:
            parent = (
                region_items.get(settlement.region_id)
                or kingdom_items.get(settlement.kingdom_id)
                or empire_items.get(settlement.empire_id)
                or continent_items.get(settlement.continent_id)
                or world_item
            )
            settlement_item = QTreeWidgetItem(["Settlement", settlement.name])
            parent.addChild(settlement_item)

        self.hierarchy_tree.expandAll()

    def create_sample_world(self) -> None:
        self.view_model.create_sample_world(
            name="New Campaign World",
            description="A fresh world generated for campaign building.",
        )
        self.refresh_world_list()

    def export_selected_world(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            return

        world_id = current_item.data(Qt.UserRole)
        if not world_id:
            return

        world = self.view_model.get_world_by_id(world_id)
        if not world:
            return

        target = Path.cwd() / f"world_export_{world.name.replace(' ', '_')}_{world.id}.json"
        self.view_model.export_full_world(world, target)
