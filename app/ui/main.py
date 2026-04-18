import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from app.core.application import ApplicationContext
from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.ui.viewmodels.world_hierarchy_viewmodel import WorldHierarchyViewModel
from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel
from app.ui.viewmodels.map_viewmodel import MapViewModel
from app.ui.viewmodels.snapshot_viewmodel import SnapshotViewModel
from app.ui.viewmodels.simulation_viewmodel import SimulationViewModel
from app.ui.views.dashboard import DashboardPage
from app.ui.views.map_view import MapViewPage
from app.ui.views.snapshots import SnapshotPage
from app.ui.views.world_generator import WorldGeneratorPage
from app.ui.views.world_hierarchy import WorldHierarchyPage
from app.ui.views.world_overview import WorldOverviewPage
from app.ui.views.simulation import SimulationPage


class WorldSimMainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        self.setWindowTitle("D&D World Simulator")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4e4bc;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(101, 67, 33, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(139, 69, 19, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(160, 82, 45, 0.05) 0%, transparent 50%);
            }
            QListWidget {
                background-color: #8b4513;
                background-image: 
                    linear-gradient(180deg, #a0522d 0%, #654321 50%, #3d2817 100%),
                    radial-gradient(circle at 30% 30%, rgba(139, 69, 19, 0.3) 0%, transparent 70%);
                color: #f4e4bc;
                border: 2px solid #654321;
                border-radius: 15px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 
                    inset 0 0 20px rgba(0, 0, 0, 0.3),
                    0 0 15px rgba(139, 69, 19, 0.4);
            }
            QListWidget::item {
                padding: 15px;
                margin: 3px 0px;
                border-radius: 8px;
                background-color: rgba(139, 69, 19, 0.2);
                border: 1px solid rgba(101, 67, 33, 0.3);
                color: #f4e4bc;
            }
            QListWidget::item:selected {
                background-color: rgba(222, 184, 135, 0.8);
                color: #654321;
                border: 2px solid #daa520;
                box-shadow: 0 0 8px rgba(218, 165, 32, 0.6);
            }
            QListWidget::item:hover {
                background-color: rgba(160, 82, 45, 0.4);
                border: 1px solid rgba(218, 165, 32, 0.5);
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation sidebar
        self.navigation = QListWidget()
        self.navigation.setFixedWidth(220)
        
        # Add navigation items with icons
        nav_items = [
            ("🏠 Dashboard", "Dashboard"),
            ("🧙‍♂️ Generator", "Generator"),
            ("🌍 Worlds", "Worlds"),
            ("📚 Hierarchy", "Hierarchy"),
            ("🎲 Simulation", "Simulation"),
            ("🗺️ Map", "Map"),
            ("📸 Snapshots", "Snapshots"),
        ]
        
        for icon_text, name in nav_items:
            item = QListWidgetItem(icon_text)
            item.setData(Qt.UserRole, name)
            self.navigation.addItem(item)
        
        layout.addWidget(self.navigation)

        # Main content area
        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f4e4bc;
                background-image: 
                    radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(160, 82, 45, 0.06) 0%, transparent 50%),
                    linear-gradient(45deg, transparent 30%, rgba(101, 67, 33, 0.03) 50%, transparent 70%);
                border: 3px solid #daa520;
                border-radius: 20px;
                margin: 15px;
                box-shadow: 
                    0 0 30px rgba(139, 69, 19, 0.4),
                    inset 0 0 20px rgba(0, 0, 0, 0.1);
                font-family: 'Times New Roman', serif;
            }
        """)
        
        self.page_stack.addWidget(DashboardPage(DashboardViewModel(self.context.persistence_service)))
        self.page_stack.addWidget(
            WorldGeneratorPage(
                WorldOverviewViewModel(
                    persistence_service=self.context.persistence_service,
                    import_export_service=self.context.import_export_service,
                )
            )
        )
        self.page_stack.addWidget(
            WorldOverviewPage(
                WorldOverviewViewModel(
                    persistence_service=self.context.persistence_service,
                    import_export_service=self.context.import_export_service,
                )
            )
        )
        self.page_stack.addWidget(
            WorldHierarchyPage(
                WorldHierarchyViewModel(
                    persistence_service=self.context.persistence_service,
                    import_export_service=self.context.import_export_service,
                )
            )
        )
        self.page_stack.addWidget(
            SimulationPage(
                SimulationViewModel(
                    persistence_service=self.context.persistence_service,
                    simulation_service=self.context.simulation_service,
                )
            )
        )
        self.page_stack.addWidget(MapViewPage(MapViewModel(self.context.persistence_service)))
        self.page_stack.addWidget(SnapshotPage(SnapshotViewModel(self.context)))
        
        layout.addWidget(self.page_stack, 1)

        self.navigation.currentRowChanged.connect(self.page_stack.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        self.setCentralWidget(central)


def main():
    app = QApplication(sys.argv)
    data_path = Path(__file__).resolve().parents[2] / "data"
    context = ApplicationContext(data_path)
    window = WorldSimMainWindow(context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
