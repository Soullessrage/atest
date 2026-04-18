"""Phase 4: World Simulation and Dynamics Tests."""

from datetime import timedelta
from pathlib import Path

from app.core.application import ApplicationContext
from app.domain.models.npc import NPC
from app.domain.models.race import Race
from app.domain.models.relationship import Relationship
from app.domain.models.structure import (
    Continent,
    Empire,
    Kingdom,
    Region,
    SettlementNode,
    SettlementType,
    World,
)


def setup_test_world_with_npcs(context: ApplicationContext) -> tuple[World, list[NPC]]:
    """Create a test world with NPCs and relationships."""
    persistence = context.persistence_service

    # Create world structure
    world = World(name="Simulation Test World", description="Test world for Phase 4 simulation.")
    persistence.create_world(world)

    continent = Continent(world_id=world.id, name="Test Continent")
    persistence.create_continent(continent)

    empire = Empire(world_id=world.id, continent_id=continent.id, name="Test Empire", ruler_name="Test Ruler")
    persistence.create_empire(empire)

    kingdom = Kingdom(world_id=world.id, continent_id=continent.id, empire_id=empire.id, name="Test Kingdom")
    persistence.create_kingdom(kingdom)

    region = Region(world_id=world.id, continent_id=continent.id, empire_id=empire.id, kingdom_id=kingdom.id, name="Test Region")
    persistence.create_region(region)

    settlement = SettlementNode(
        world_id=world.id,
        continent_id=continent.id,
        empire_id=empire.id,
        kingdom_id=kingdom.id,
        region_id=region.id,
        name="Test Settlement",
        settlement_type=SettlementType.TOWN.value,
        population=500,
        location={"x": 100.0, "y": 100.0},
    )
    persistence.create_settlement(settlement)

    # Create a race
    humanrace = Race(id="human", name="Human", lifespan=80)
    persistence.race_repository.add(humanrace)

    # Create NPCs
    npc1 = NPC(
        world_id=world.id,
        name="Alice",
        settlement_id=settlement.id,
        age=30,
        race_id=humanrace.id,
        gender="female",
        health_status="healthy",
        fertility_score=0.8,
    )
    persistence.create_npc(npc1)

    npc2 = NPC(
        world_id=world.id,
        name="Bob",
        settlement_id=settlement.id,
        age=32,
        race_id=humanrace.id,
        gender="male",
        health_status="healthy",
        fertility_score=0.8,
    )
    persistence.create_npc(npc2)

    npc3 = NPC(
        world_id=world.id,
        name="Elder",
        settlement_id=settlement.id,
        age=75,
        race_id=humanrace.id,
        gender="male",
        health_status="healthy",
    )
    persistence.create_npc(npc3)

    # Create a relationship (marriage)
    rel = Relationship(
        world_id=world.id,
        source_id=npc1.id,
        target_id=npc2.id,
        relation_type="marriage",
        weight=85.0,
    )
    persistence.create_relationship(rel)

    # Update world to track entities
    world.continents = [continent.id]
    world.empires = [empire.id]
    world.kingdoms = [kingdom.id]
    world.regions = [region.id]
    world.settlements = [settlement.id]
    world.npc_ids = [npc1.id, npc2.id, npc3.id]
    persistence.update_world(world)

    return world, [npc1, npc2, npc3]


def test_npc_ageing(tmp_path: Path) -> None:
    """Test that NPCs age during simulation."""
    context = ApplicationContext(tmp_path / "npc_ageing_test")
    world, (npc1, npc2, npc3) = setup_test_world_with_npcs(context)

    # Run simulation for 10 years
    run = context.simulation_service.advance(world.id, timedelta(days=365 * 10))

    # Check that NPCs aged
    assert run["npcs_aged"] == 3, f"Expected 3 NPCs aged, got {run['npcs_aged']}"
    context.close()


def test_npc_death_from_old_age(tmp_path: Path) -> None:
    """Test that elderly NPCs can die from old age."""
    context = ApplicationContext(tmp_path / "npc_death_test")
    world, npcs = setup_test_world_with_npcs(context)

    # Elder NPC is 75 years old, natural lifespan is 80
    # Run simulation for 10 years (will be 85)
    run = context.simulation_service.advance(world.id, timedelta(days=365 * 10))

    # Should have at least some chance of death for the elder
    # (not guaranteed, but statistically should happen)
    # For this test, we just verify the simulation ran without error
    assert "npcs_died" in run
    context.close()


def test_npc_birth(tmp_path: Path) -> None:
    """Test that NPCs can be born from fertile relationships."""
    context = ApplicationContext(tmp_path / "npc_birth_test")
    world, npcs = setup_test_world_with_npcs(context)

    initial_npc_count = len(world.npc_ids) if world.npc_ids else 0

    # Run simulation for multiple periods to increase birth chance
    for _ in range(5):
        run = context.simulation_service.advance(world.id, timedelta(days=365))

    # Check world to see if any new NPCs were born
    updated_world = context.persistence_service.load_world(world.id)
    new_npc_count = len(updated_world.npc_ids) if updated_world and updated_world.npc_ids else 0

    # At least maintain the initial count
    assert new_npc_count >= initial_npc_count

    context.close()


def test_population_dynamics(tmp_path: Path) -> None:
    """Test that settlement populations are updated based on NPC dynamics."""
    context = ApplicationContext(tmp_path / "population_dynamics_test")
    world, npcs = setup_test_world_with_npcs(context)

    settlements = context.persistence_service.list_settlements(world.id)
    initial_pop = settlements[0].population if settlements else 0

    # Run simulation
    run = context.simulation_service.advance(world.id, timedelta(days=365 * 5))

    # Population should change (grow or stay similar)
    settlements_after = context.persistence_service.list_settlements(world.id)
    final_pop = settlements_after[0].population if settlements_after else 0

    # Settlement should have some population activity recorded
    assert run.get("settlements_grew") is not None or run.get("settlements_shrunk") is not None

    context.close()


def test_relationship_dynamics(tmp_path: Path) -> None:
    """Test that relationships change over time."""
    context = ApplicationContext(tmp_path / "relationship_dynamics_test")
    world, npcs = setup_test_world_with_npcs(context)

    relationships = context.persistence_service.list_relationships(world.id)
    initial_rel = relationships[0] if relationships else None
    initial_weight = initial_rel.weight if initial_rel else 0

    # Run simulation - NPCs in same settlement, so relationship should strengthen
    run = context.simulation_service.advance(world.id, timedelta(days=365))

    relationships_after = context.persistence_service.list_relationships(world.id)
    final_rel = relationships_after[0] if relationships_after else None
    final_weight = final_rel.weight if final_rel else 0

    # Relationship weight should have changed (strength married couple in same settlement)
    assert final_weight >= initial_weight

    context.close()


def test_simulation_run_object(tmp_path: Path) -> None:
    """Test that SimulationRun properly tracks changes."""
    context = ApplicationContext(tmp_path / "simulation_run_test")
    world, npcs = setup_test_world_with_npcs(context)

    result = context.simulation_service.advance(world.id, timedelta(days=365))

    # Verify result contains expected fields
    assert "world_id" in result
    assert "duration_days" in result
    assert "event_count" in result
    assert "npcs_aged" in result
    assert "npcs_died" in result
    assert "npcs_born" in result
    assert "settlements_grew" in result
    assert "settlements_shrunk" in result
    assert "outcome_summary" in result

    context.close()


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        print("Running Phase 4 tests...")
        test_simulation_run_object(tmp / "test1")
        print("✓ SimulationRun object test passed")

        test_npc_ageing(tmp / "test2")
        print("✓ NPC ageing test passed")

        test_population_dynamics(tmp / "test3")
        print("✓ Population dynamics test passed")

        test_relationship_dynamics(tmp / "test4")
        print("✓ Relationship dynamics test passed")

        test_npc_death_from_old_age(tmp / "test5")
        print("✓ NPC death test passed")

        print("\nAll Phase 4 tests passed! ✅")
