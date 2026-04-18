from __future__ import annotations

from pathlib import Path
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.viewmodels.world_hierarchy_viewmodel import WorldHierarchyViewModel


class WorldHierarchyPage(QWidget):
    def __init__(self, view_model: WorldHierarchyViewModel):
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
                background: linear-gradient(135deg, #8e44ad 0%, #3498db 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title = QLabel("📚 World Hierarchy")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Browse your world state as a hierarchical tree.")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 16px;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_frame)

        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 18px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)

        world_label = QLabel("🌍 Select World:")
        world_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-right: 12px;
            }
        """)

        self.world_selector = QComboBox()
        self.world_selector.setMinimumWidth(260)
        self.world_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.world_selector.currentIndexChanged.connect(self.on_world_selected)

        self.refresh_button = QPushButton("🔄 Refresh")
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
        """)
        self.refresh_button.clicked.connect(self.refresh_world_selector)

        self.export_button = QPushButton("📤 Export World")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.export_button.clicked.connect(self.export_selected_world)

        self.import_button = QPushButton("📥 Import World")
        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        self.import_button.clicked.connect(self.import_world_file)

        control_layout.addWidget(world_label)
        control_layout.addWidget(self.world_selector)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.export_button)
        control_layout.addWidget(self.import_button)

        layout.addWidget(control_frame)

        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 14px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter hierarchy by name or type...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tree)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 13px;
            }
        """)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(self.status_label)
        layout.addWidget(filter_frame)

        self.summary_label = QLabel("Select a world to visualize its continent, empire, kingdom, region, and settlement structure.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.summary_label)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.count_label)

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
        self.hierarchy_tree.setIndentation(16)
        layout.addWidget(self.hierarchy_tree, 1)

    def refresh_world_selector(self) -> None:
        active_id = self.world_selector.currentData()
        self.world_selector.blockSignals(True)
        self.world_selector.clear()
        self.world_selector.addItem("Select a world...", None)
        for world in self.view_model.list_worlds():
            self.world_selector.addItem(world.name, world.id)
        self.world_selector.blockSignals(False)

        if active_id is not None:
            index = self.world_selector.findData(active_id)
            if index != -1:
                self.world_selector.setCurrentIndex(index)
                return

        if self.world_selector.count() > 1:
            self.world_selector.setCurrentIndex(1)
        else:
            self.render_hierarchy(None)

    def on_world_selected(self) -> None:
        world_id = self.world_selector.currentData()
        if world_id is None:
            self.render_hierarchy(None)
            return

        details = self.view_model.load_world_details(world_id)
        self.render_hierarchy(details)

    def render_hierarchy(self, details: dict | None) -> None:
        self.hierarchy_tree.clear()
        if details is None or details.get("world") is None:
            self.summary_label.setText("Select a world to visualize its hierarchy.")
            self.count_label.setText("")
            return

        world = details["world"]
        continents = details["continents"]
        empires = details["empires"]
        kingdoms = details["kingdoms"]
        regions = details["regions"]
        settlements = details["settlements"]

        self.summary_label.setText(f"<b>{world.name}</b> — {world.description or 'A structured world hierarchy view.'}")
        self.count_label.setText(
            f"Continents: {len(continents)} | Empires: {len(empires)} | Kingdoms: {len(kingdoms)} | Regions: {len(regions)} | Settlements: {len(settlements)}"
        )

        world_item = QTreeWidgetItem(["World", world.name])
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
            parent = (
                kingdom_items.get(region.kingdom_id)
                or empire_items.get(region.empire_id)
                or continent_items.get(region.continent_id)
                or world_item
            )
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
        self.filter_tree(self.search_input.text())

    def export_selected_world(self) -> None:
        world_id = self.world_selector.currentData()
        if world_id is None:
            self.status_label.setText("Please choose a world before exporting.")
            return

        target_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export World Package",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not target_path:
            return

        try:
            self.view_model.export_world(world_id, Path(target_path))
            self.status_label.setText("Export complete.")
        except Exception as exc:
            self.status_label.setText(f"Export failed: {exc}")

    def import_world_file(self) -> None:
        source_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import World Package",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not source_path:
            return

        try:
            imported = self.view_model.import_world(Path(source_path))
            self.status_label.setText(f"Imported world: {imported.name}")
            self.refresh_world_selector()
            index = self.world_selector.findData(imported.id)
            if index != -1:
                self.world_selector.setCurrentIndex(index)
        except Exception as exc:
            self.status_label.setText(f"Import failed: {exc}")

    def filter_tree(self, query: str) -> None:
        query = query.strip().lower()
        for i in range(self.hierarchy_tree.topLevelItemCount()):
            item = self.hierarchy_tree.topLevelItem(i)
            visible = self._filter_item(item, query)
            item.setHidden(not visible)

    def _filter_item(self, item: QTreeWidgetItem, query: str) -> bool:
        item_text = " ".join(item.text(col) for col in range(item.columnCount())).lower()
        matches = query in item_text if query else True
        child_visible = False
        for i in range(item.childCount()):
            child = item.child(i)
            if self._filter_item(child, query):
                child_visible = True
        item.setHidden(not (matches or child_visible))
        item.setExpanded(child_visible)
        return matches or child_visible
