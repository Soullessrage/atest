from pathlib import Path

from app.core.application import ApplicationContext
from app.domain.models.structure import (
    Continent,
    Empire,
    Kingdom,
    Region,
    SettlementNode,
    SettlementType,
    World,
)


def create_test_world(context: ApplicationContext) -> World:
    persistence = context.persistence_service

    world = World(name="Test World", description="A hierarchical test world.")
    persistence.create_world(world)

    continent = Continent(world_id=world.id, name="Terra")
    persistence.create_continent(continent)

    empire = Empire(
        world_id=world.id,
        continent_id=continent.id,
        name="Atlas Realm",
        ruler_name="Queen Mira",
    )
    persistence.create_empire(empire)

    kingdom = Kingdom(
        world_id=world.id,
        continent_id=continent.id,
        empire_id=empire.id,
        name="Deepwood",
    )
    persistence.create_kingdom(kingdom)

    region = Region(
        world_id=world.id,
        continent_id=continent.id,
        empire_id=empire.id,
        kingdom_id=kingdom.id,
        name="Silverwood",
    )
    persistence.create_region(region)

    settlement = SettlementNode(
        world_id=world.id,
        continent_id=continent.id,
        empire_id=empire.id,
        kingdom_id=kingdom.id,
        region_id=region.id,
        name="Fort Dawn",
        settlement_type=SettlementType.FORTRESS.value,
        population=1200,
        location={"x": 120.0, "y": 220.0},
    )
    persistence.create_settlement(settlement)

    continent.empire_ids = [empire.id]
    continent.kingdom_ids = [kingdom.id]
    continent.region_ids = [region.id]
    continent.settlement_ids = [settlement.id]
    persistence.update_continent(continent)

    empire.kingdom_ids = [kingdom.id]
    persistence.update_empire(empire)

    kingdom.region_ids = [region.id]
    kingdom.capital_settlement_id = settlement.id
    persistence.update_kingdom(kingdom)

    region.settlement_ids = [settlement.id]
    persistence.update_region(region)

    world.continents = [continent.id]
    world.empires = [empire.id]
    world.kingdoms = [kingdom.id]
    world.regions = [region.id]
    world.settlements = [settlement.id]
    persistence.update_world(world)

    return world


def test_export_import_full_world_state(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    source_context = ApplicationContext(source_root)
    world = create_test_world(source_context)
    package_file = source_root / "world_export_test.json"
    source_context.import_export_service.export_full_world(world.id, package_file)

    target_context = ApplicationContext(target_root)
    imported_world = target_context.import_export_service.import_world(package_file)

    assert imported_world.id == world.id
    assert imported_world.name == world.name
    assert imported_world.description == world.description
    assert len(target_context.persistence_service.list_continents(world.id)) == 1
    assert len(target_context.persistence_service.list_empires(world.id)) == 1
    assert len(target_context.persistence_service.list_kingdoms(world.id)) == 1
    assert len(target_context.persistence_service.list_regions(world.id)) == 1
    assert len(target_context.persistence_service.list_settlements(world.id)) == 1

    source_context.close()
    target_context.close()


def test_snapshot_create_and_restore(tmp_path: Path) -> None:
    root = tmp_path / "snapshot_test"
    context = ApplicationContext(root)
    world = create_test_world(context)
    snapshot = context.snapshot_manager.create_snapshot(world.id, "Initial Save")

    assert snapshot.id.startswith("snapshot-")
    assert snapshot.file_path.exists()

    restored_world = context.snapshot_manager.restore_snapshot(snapshot.id)
    assert restored_world.id == world.id
    assert restored_world.name == world.name
    assert len(context.persistence_service.list_continents(world.id)) == 1
    assert len(context.persistence_service.list_empires(world.id)) == 1
    assert len(context.persistence_service.list_kingdoms(world.id)) == 1
    assert len(context.persistence_service.list_regions(world.id)) == 1
    assert len(context.persistence_service.list_settlements(world.id)) == 1

    context.close()
