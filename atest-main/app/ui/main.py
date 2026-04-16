import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.core.application import ApplicationContext
from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel
from app.ui.viewmodels.map_viewmodel import MapViewModel
from app.ui.viewmodels.snapshot_viewmodel import SnapshotViewModel
from app.ui.views.dashboard import DashboardPage
from app.ui.views.map_view import MapViewPage
from app.ui.views.snapshots import SnapshotPage
from app.ui.views.world_overview import WorldOverviewPage
from app.core.simulation.service import SimulationService


class WorldSimMainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        self.setWindowTitle("DND World Simulator")
        self.setMinimumSize(1200, 800)

        # Create simulation service once
        self.simulation = SimulationService()

        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)

        # Navigation list
        self.navigation = QListWidget()
        self.navigation.addItems(["Dashboard", "Worlds", "Map", "Snapshots"])
        self.navigation.setFixedWidth(180)
        layout.addWidget(self.navigation)

        # Page stack
        self.page_stack = QStackedWidget()

        # Dashboard now receives simulation service
        self.page_stack.addWidget(
            DashboardPage(
                DashboardViewModel(self.context.persistence_service),
                self.simulation
            )
        )

        # Other pages unchanged
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

        # Navigation behavior
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
