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
from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel
from app.ui.viewmodels.map_viewmodel import MapViewModel
from app.ui.viewmodels.snapshot_viewmodel import SnapshotViewModel
from app.ui.views.dashboard import DashboardPage
from app.ui.views.map_view import MapViewPage
from app.ui.views.snapshots import SnapshotPage
from app.ui.views.world_overview import WorldOverviewPage


class WorldSimMainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        self.setWindowTitle("D&D World Simulator")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 500;
            }
            QListWidget::item {
                padding: 12px;
                margin: 2px 0px;
                border-radius: 6px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #34495e;
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
            ("🌍 Worlds", "Worlds"), 
            ("🗺️ Map", "Map"),
            ("📸 Snapshots", "Snapshots")
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
                background-color: white;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        
        self.page_stack.addWidget(DashboardPage(DashboardViewModel(self.context.persistence_service)))
        self.page_stack.addWidget(
            WorldOverviewPage(
                WorldOverviewViewModel(
                    persistence_service=self.context.persistence_service,
                    import_export_service=self.context.import_export_service,
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
