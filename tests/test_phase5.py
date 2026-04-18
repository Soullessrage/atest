"""Phase 5: Simulation UI Integration Tests."""

import pytest
from unittest.mock import Mock

from app.core.services.persistence_service import PersistenceService
from app.core.services.simulation_service import SimulationService
from app.ui.viewmodels.simulation_viewmodel import SimulationViewModel
from app.domain.models.structure import World


def test_simulation_viewmodel_creation():
    """Test that SimulationViewModel can be created."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    view_model = SimulationViewModel(mock_persistence, mock_simulation)

    assert view_model.persistence_service == mock_persistence
    assert view_model.simulation_service == mock_simulation
    assert view_model.worlds == []
    assert view_model.selected_world is None
    assert view_model.simulation_history == []
    assert view_model.current_run is None
    assert not view_model.is_running


def test_simulation_viewmodel_load_worlds():
    """Test loading worlds in the view model."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    # Mock worlds
    worlds = [
        World(name="World 1", description="Test world 1"),
        World(name="World 2", description="Test world 2"),
    ]
    mock_persistence.list_worlds.return_value = worlds

    view_model = SimulationViewModel(mock_persistence, mock_simulation)

    # Test signal connection
    signal_received = []
    view_model.worlds_loaded.connect(lambda w: signal_received.append(w))

    # Load worlds
    view_model.load_worlds()

    # Verify persistence service was called
    mock_persistence.list_worlds.assert_called_once()

    # Verify worlds were stored
    assert view_model.worlds == worlds

    # Verify signal was emitted
    assert len(signal_received) == 1
    assert signal_received[0] == worlds


def test_simulation_viewmodel_select_world():
    """Test selecting a world."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    worlds = [
        World(id="world1", name="World 1"),
        World(id="world2", name="World 2"),
    ]

    view_model = SimulationViewModel(mock_persistence, mock_simulation)
    view_model.worlds = worlds

    # Select world
    view_model.select_world("world1")

    assert view_model.selected_world == worlds[0]

    # Select non-existent world
    view_model.select_world("nonexistent")
    assert view_model.selected_world is None


def test_simulation_viewmodel_run_simulation():
    """Test running a simulation."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    # Mock world and simulation run
    world = World(id="world1", name="Test World")
    mock_run = Mock()
    mock_simulation.advance.return_value = mock_run
    mock_persistence.load_world.return_value = world

    view_model = SimulationViewModel(mock_persistence, mock_simulation)
    view_model.selected_world = world

    # Test signal connections
    signals_received = []
    view_model.simulation_started.connect(lambda: signals_received.append("started"))
    view_model.simulation_completed.connect(lambda r: signals_received.append(("completed", r)))

    # Run simulation
    view_model.run_simulation(days=365)

    # Verify simulation service was called
    from datetime import timedelta
    mock_simulation.advance.assert_called_once_with("world1", timedelta(days=365))

    # Verify signals were emitted
    assert "started" in signals_received
    assert ("completed", mock_run) in [s for s in signals_received if isinstance(s, tuple)]

    # Verify run was stored
    assert view_model.current_run == mock_run
    assert mock_run in view_model.simulation_history


def test_simulation_viewmodel_run_simulation_no_world():
    """Test running simulation without selecting a world."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    view_model = SimulationViewModel(mock_persistence, mock_simulation)

    # Test signal connection
    error_received = []
    view_model.simulation_error.connect(lambda e: error_received.append(e))

    # Try to run simulation without selecting world
    view_model.run_simulation()

    # Verify error was emitted
    assert len(error_received) == 1
    assert "No world selected" in error_received[0]

    # Verify simulation service was not called
    mock_simulation.advance.assert_not_called()


def test_simulation_viewmodel_run_simulation_already_running():
    """Test running simulation when one is already running."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    view_model = SimulationViewModel(mock_persistence, mock_simulation)
    view_model.selected_world = World(id="world1", name="Test World")
    view_model.is_running = True

    # Test signal connection
    error_received = []
    view_model.simulation_error.connect(lambda e: error_received.append(e))

    # Try to run simulation while one is running
    view_model.run_simulation()

    # Verify error was emitted
    assert len(error_received) == 1
    assert "already running" in error_received[0]

    # Verify simulation service was not called
    mock_simulation.advance.assert_not_called()


def test_simulation_viewmodel_clear_history():
    """Test clearing simulation history."""
    mock_persistence = Mock(spec=PersistenceService)
    mock_simulation = Mock(spec=SimulationService)

    view_model = SimulationViewModel(mock_persistence, mock_simulation)

    # Add some mock history
    mock_run1 = Mock()
    mock_run2 = Mock()
    view_model.simulation_history = [mock_run1, mock_run2]
    view_model.current_run = mock_run2

    # Clear history
    view_model.clear_history()

    # Verify history was cleared
    assert view_model.simulation_history == []
    assert view_model.current_run is None