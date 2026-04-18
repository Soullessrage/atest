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

        title = QLabel("📚 World Hierarchy")
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

        subtitle = QLabel("Browse your world state as a hierarchical tree.")
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

        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(139, 69, 19, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(160, 82, 45, 0.08) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
        """)
        control_layout = QHBoxLayout(control_frame)

        world_label = QLabel("🌍 Select World:")
        world_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                margin-right: 12px;
            }
        """)

        self.world_selector = QComboBox()
        self.world_selector.setMinimumWidth(260)
        self.world_selector.setStyleSheet("""
            QComboBox {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 10px 12px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
            }
            QComboBox:hover {
                border-color: #cd853f;
                background-color: rgba(222, 184, 135, 0.9);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(244, 228, 188, 0.95);
                border: 1px solid #daa520;
                selection-background-color: rgba(205, 133, 63, 0.8);
                color: #654321;
            }
        """)
        self.world_selector.currentIndexChanged.connect(self.on_world_selected)

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #daa520;
                background-image: linear-gradient(180deg, #daa520 0%, #cd853f 100%);
                color: #654321;
                border: 2px solid #a0522d;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 8px rgba(139, 69, 19, 0.4);
            }
            QPushButton:hover {
                background-color: #cd853f;
                background-image: linear-gradient(180deg, #cd853f 0%, #a0522d 100%);
                border-color: #8b4513;
                box-shadow: 0 0 12px rgba(139, 69, 19, 0.6);
            }
            QPushButton:pressed {
                background-color: #a0522d;
                transform: translateY(1px);
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_world_selector)

        self.export_button = QPushButton("📤 Export World")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #228b22;
                background-image: linear-gradient(180deg, #32cd32 0%, #228b22 100%);
                color: #f4e4bc;
                border: 2px solid #006400;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 8px rgba(34, 139, 34, 0.4);
            }
            QPushButton:hover {
                background-color: #32cd32;
                background-image: linear-gradient(180deg, #32cd32 0%, #006400 100%);
                border-color: #228b22;
                box-shadow: 0 0 12px rgba(34, 139, 34, 0.6);
            }
            QPushButton:pressed {
                background-color: #006400;
                transform: translateY(1px);
            }
        """)
        self.export_button.clicked.connect(self.export_selected_world)

        self.import_button = QPushButton("📥 Import World")
        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #8b4513;
                background-image: linear-gradient(180deg, #a0522d 0%, #8b4513 100%);
                color: #f4e4bc;
                border: 2px solid #654321;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 8px rgba(139, 69, 19, 0.4);
            }
            QPushButton:hover {
                background-color: #a0522d;
                background-image: linear-gradient(180deg, #a0522d 0%, #654321 100%);
                border-color: #3d2817;
                box-shadow: 0 0 12px rgba(139, 69, 19, 0.6);
            }
            QPushButton:pressed {
                background-color: #654321;
                transform: translateY(1px);
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
                background-color: rgba(244, 228, 188, 0.9);
                background-image: 
                    radial-gradient(circle at 30% 70%, rgba(139, 69, 19, 0.08) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 
                    0 0 10px rgba(139, 69, 19, 0.2),
                    inset 0 0 8px rgba(0, 0, 0, 0.05);
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter hierarchy by name or type...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                background-color: rgba(244, 228, 188, 0.9);
                color: #654321;
            }
            QLineEdit:focus {
                border-color: #cd853f;
                background-color: rgba(222, 184, 135, 0.9);
                box-shadow: 0 0 8px rgba(218, 165, 32, 0.4);
            }
            QLineEdit::placeholder {
                color: rgba(101, 67, 33, 0.6);
                font-style: italic;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tree)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #8b4513;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
            }
        """)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(self.status_label)
        layout.addWidget(filter_frame)

        self.summary_label = QLabel("Select a world to visualize its continent, empire, kingdom, region, and settlement structure.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #654321;
                font-size: 16px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                background-color: rgba(244, 228, 188, 0.8);
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(218, 165, 32, 0.3);
            }
        """)
        layout.addWidget(self.summary_label)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("""
            QLabel {
                color: #8b4513;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                background-color: rgba(244, 228, 188, 0.9);
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid rgba(218, 165, 32, 0.4);
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.count_label)

        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabels(["Type", "Name"])
        self.hierarchy_tree.setStyleSheet("""
            QTreeWidget {
                border: 3px solid #daa520;
                border-radius: 12px;
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 10% 10%, rgba(139, 69, 19, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 90%, rgba(160, 82, 45, 0.03) 0%, transparent 40%);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
                alternate-background-color: rgba(222, 184, 135, 0.3);
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(218, 165, 32, 0.2);
            }
            QTreeWidget::item:selected {
                background-color: rgba(205, 133, 63, 0.8);
                color: #f4e4bc;
                border: 1px solid #daa520;
            }
            QTreeWidget::item:hover {
                background-color: rgba(222, 184, 135, 0.5);
            }
            QHeaderView::section {
                background-color: rgba(139, 69, 19, 0.8);
                color: #f4e4bc;
                padding: 8px;
                border: 1px solid #daa520;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
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
