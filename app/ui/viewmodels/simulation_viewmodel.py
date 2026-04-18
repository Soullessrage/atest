from __future__ import annotations

from datetime import timedelta
from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from app.core.services.persistence_service import PersistenceService
from app.core.services.simulation_service import SimulationService
from app.domain.models.structure import World
from app.domain.simulation.runner import SimulationRun


class SimulationViewModel(QObject):
    """
    View model for simulation controls and results.

    Manages:
    - World selection for simulation
    - Running simulations with different time periods
    - Tracking simulation history and results
    - Progress updates during simulation
    """

    # Signals
    worlds_loaded = Signal(list)  # List[World]
    simulation_started = Signal()
    simulation_progress = Signal(str)  # Progress message
    simulation_completed = Signal(object)  # SimulationRun
    simulation_error = Signal(str)  # Error message

    def __init__(self, persistence_service: PersistenceService, simulation_service: SimulationService):
        super().__init__()
        self.persistence_service = persistence_service
        self.simulation_service = simulation_service

        self.worlds: List[World] = []
        self.selected_world: Optional[World] = None
        self.simulation_history: List[SimulationRun] = []
        self.current_run: Optional[SimulationRun] = None
        self.is_running = False

    def load_worlds(self) -> None:
        """Load all available worlds for simulation."""
        try:
            self.worlds = self.persistence_service.list_worlds()
            self.worlds_loaded.emit(self.worlds)
        except Exception as e:
            self.simulation_error.emit(f"Failed to load worlds: {str(e)}")

    def select_world(self, world_id: str) -> None:
        """Select a world for simulation."""
        self.selected_world = next((w for w in self.worlds if w.id == world_id), None)

    def run_simulation(self, days: int = 365) -> None:
        """Run simulation for the selected world."""
        if not self.selected_world:
            self.simulation_error.emit("No world selected")
            return

        if self.is_running:
            self.simulation_error.emit("Simulation already running")
            return

        try:
            self.is_running = True
            self.simulation_started.emit()
            self.simulation_progress.emit("Starting simulation...")

            # Run the simulation
            duration = timedelta(days=days)
            run = self.simulation_service.advance(self.selected_world.id, duration)

            # Update our state
            self.current_run = run
            self.simulation_history.append(run)
            self.is_running = False

            # Reload the world to get updated state
            updated_world = self.persistence_service.load_world(self.selected_world.id)
            if updated_world:
                self.selected_world = updated_world

            self.simulation_completed.emit(run)

        except Exception as e:
            self.is_running = False
            self.simulation_error.emit(f"Simulation failed: {str(e)}")

    def get_simulation_results(self) -> Optional[SimulationRun]:
        """Get the results of the most recent simulation."""
        return self.current_run

    def get_simulation_history(self) -> List[SimulationRun]:
        """Get the history of all simulations run in this session."""
        return self.simulation_history.copy()

    def clear_history(self) -> None:
        """Clear the simulation history."""
        self.simulation_history.clear()
        self.current_run = None