"""Phase 6: Advanced World Generation Tests."""

import pytest

from app.core.application import ApplicationContext
from app.domain.generation.params import WorldGenerationParams
from app.domain.generation.service import WorldGenerationService


def test_world_generation_params_creation():
    """Test creating world generation parameters."""
    params = WorldGenerationParams(
        name="Test World",
        description="A test world",
        continent_count=5,
        climate="tropical",
        complexity_modifier=1.5,
    )

    assert params.name == "Test World"
    assert params.continent_count == 5
    assert params.climate == "tropical"
    assert params.complexity_modifier == 1.5


def test_world_generation_params_bounds():
    """Test that parameters are bounded correctly."""
    # Test size modifier bounds
    params_small = WorldGenerationParams(name="Small", description="", size_modifier=0.1)
    assert params_small.size_modifier == 0.5  # Bounded to minimum

    params_large = WorldGenerationParams(name="Large", description="", size_modifier=5.0)
    assert params_large.size_modifier == 3.0  # Bounded to maximum


def test_world_generation_params_calculations():
    """Test parameter-based calculations."""
    params = WorldGenerationParams(
        name="Test",
        description="",
        continent_count=6,
        complexity_modifier=2.0,
    )

    # Empire count should be based on continents and complexity
    empire_count = params.get_empire_count()
    assert empire_count > 0

    # Settlement count should scale with complexity
    settlement_count = params.get_settlement_per_region()
    assert settlement_count >= 3  # At least base amount

    # NPC modifier should match complexity
    npc_modifier = params.get_npc_per_settlement_modifier()
    assert npc_modifier == 2.0


def test_world_generation_service_creation():
    """Test that WorldGenerationService can be created."""
    from unittest.mock import Mock

    mock_persistence = Mock()
    service = WorldGenerationService(mock_persistence)

    assert service.persistence_service == mock_persistence
    assert service.generated_world is None


def test_basic_world_generation(context: ApplicationContext):
    """Test basic world generation."""
    persistence = context.persistence_service
    service = WorldGenerationService(persistence)

    params = WorldGenerationParams(
        name="Test Generated World",
        description="A procedurally generated test world",
        continent_count=3,
        complexity_modifier=1.0,
    )

    world = service.generate_world(params)

    # Verify world was created
    assert world is not None
    assert world.name == "Test Generated World"
    assert world.description == "A procedurally generated test world"

    # Verify world has continents
    assert len(world.continents) == 3

    # Verify continents were persisted
    continents = persistence.list_continents(world.id)
    assert len(continents) == 3

    # Verify at least one empire was created
    empires = persistence.list_empires(world.id)
    assert len(empires) > 0

    # Verify kingdoms were created
    kingdoms = persistence.list_kingdoms(world.id)
    assert len(kingdoms) > 0

    # Verify regions were created
    regions = persistence.list_regions(world.id)
    assert len(regions) > 0

    # Verify settlements were created
    settlements = persistence.list_settlements(world.id)
    assert len(settlements) > 0


def test_world_generation_with_high_complexity(context: ApplicationContext):
    """Test world generation with higher complexity."""
    persistence = context.persistence_service
    service = WorldGenerationService(persistence)

    params = WorldGenerationParams(
        name="Complex World",
        description="High complexity world",
        continent_count=4,
        complexity_modifier=2.0,
        size_modifier=1.5,
    )

    world = service.generate_world(params)

    # Should have more empires, kingdoms, regions, settlements with higher complexity
    empires = persistence.list_empires(world.id)
    kingdoms = persistence.list_kingdoms(world.id)
    regions = persistence.list_regions(world.id)
    settlements = persistence.list_settlements(world.id)

    assert len(empires) > 0
    assert len(kingdoms) >= len(empires) * 2
    assert len(regions) > len(kingdoms)
    assert len(settlements) > len(regions)


def test_world_generation_npc_creation(context: ApplicationContext):
    """Test that NPCs are created during world generation."""
    persistence = context.persistence_service
    service = WorldGenerationService(persistence)

    params = WorldGenerationParams(
        name="NPC Test World",
        description="World for NPC generation testing",
        continent_count=1,
        complexity_modifier=1.0,
    )

    world = service.generate_world(params)

    # Verify NPCs were created
    assert len(world.npc_ids) > 0

    # Verify NPCs are in persistence
    npcs = persistence.list_npcs(world.id)
    assert len(npcs) > 0


@pytest.fixture
def context():
    """Create an application context for testing."""
    from pathlib import Path

    data_path = Path(__file__).resolve().parent.parent / "tests" / "data" / "test_phase6"
    context = ApplicationContext(data_path)
    yield context
    # Cleanup could be done here if needed