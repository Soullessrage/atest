from __future__ import annotations

import random
from typing import Optional

from app.core.services.persistence_service import PersistenceService
from app.domain.generation.params import WorldGenerationParams
from app.domain.models.structure import (
    World,
    Continent,
    Empire,
    Kingdom,
    Region,
    SettlementNode,
    SettlementType,
    Route,
)
from app.domain.models.npc import NPC
from app.domain.models.race import Race


class WorldGenerationService:
    """Procedurally generates complete D&D worlds with all hierarchical structures."""

    def __init__(self, persistence_service: PersistenceService):
        self.persistence_service = persistence_service
        self.generated_world: Optional[World] = None

    def generate_world(self, params: WorldGenerationParams) -> World:
        """Generate a complete world with all structures based on parameters."""
        # Create the world
        self.generated_world = World(name=params.name, description=params.description)
        self.persistence_service.create_world(self.generated_world)

        # Generate geographic structure
        self._generate_continents(params)

        # Generate political structure
        self._generate_political_structure(params)

        # Generate settlements and settlements networks
        self._generate_settlements(params)

        # Generate settlement connections
        self._generate_routes(params)

        # Generate initial NPCs
        self._generate_npcs(params)

        # Update world totals
        self._update_world_totals()

        return self.generated_world

    def _generate_continents(self, params: WorldGenerationParams) -> None:
        """Generate continents for the world."""
        if not self.generated_world:
            return

        climate_types = {
            "temperate": ["Temperate"],
            "tropical": ["Tropical"],
            "arid": ["Arid", "Desert"],
            "polar": ["Polar", "Tundra"],
            "mixed": ["Temperate", "Tropical", "Arid", "Polar"],
        }

        climates = climate_types.get(params.climate, ["Temperate"])

        for i in range(params.continent_count):
            continent = Continent(
                world_id=self.generated_world.id,
                name=self._generate_continent_name(i),
                description=f"A major continent with {random.choice(climates)} climate.",
            )
            self.persistence_service.create_continent(continent)
            self.generated_world.continents.append(continent.id)

    def _generate_political_structure(self, params: WorldGenerationParams) -> None:
        """Generate empires, kingdoms, and political structure."""
        if not self.generated_world:
            return

        continents = self.persistence_service.list_continents(self.generated_world.id)
        empires_per_continent = max(1, params.get_empire_count() // len(continents))

        empire_count = 0
        for continent in continents:
            for _ in range(empires_per_continent):
                empire = Empire(
                    world_id=self.generated_world.id,
                    continent_id=continent.id,
                    name=self._generate_empire_name(),
                    ruler_name=self._generate_ruler_name(),
                )
                self.persistence_service.create_empire(empire)
                continent.empire_ids.append(empire.id)
                self.generated_world.empires.append(empire.id)

                # Generate kingdoms within empire
                kingdom_count = max(2, int(3 * params.complexity_modifier))
                for _ in range(kingdom_count):
                    kingdom = Kingdom(
                        world_id=self.generated_world.id,
                        continent_id=continent.id,
                        empire_id=empire.id,
                        name=self._generate_kingdom_name(),
                    )
                    self.persistence_service.create_kingdom(kingdom)
                    continent.kingdom_ids.append(kingdom.id)
                    empire.kingdom_ids.append(kingdom.id)
                    self.generated_world.kingdoms.append(kingdom.id)

                    # Generate regions within kingdom
                    region_count = max(1, int(2 * params.complexity_modifier))
                    for _ in range(region_count):
                        region = Region(
                            world_id=self.generated_world.id,
                            continent_id=continent.id,
                            empire_id=empire.id,
                            kingdom_id=kingdom.id,
                            name=self._generate_region_name(),
                        )
                        self.persistence_service.create_region(region)
                        continent.region_ids.append(region.id)
                        kingdom.region_ids.append(region.id)
                        self.generated_world.regions.append(region.id)

                empire_count += 1

            # Update continent in persistence
            self.persistence_service.update_continent(continent)

    def _generate_settlements(self, params: WorldGenerationParams) -> None:
        """Generate settlements within regions."""
        if not self.generated_world:
            return

        regions = self.persistence_service.list_regions(self.generated_world.id)

        for region in regions:
            settlement_count = params.get_settlement_per_region()

            for i in range(settlement_count):
                # Vary settlement types
                settlement_types = [
                    SettlementType.VILLAGE.value,
                    SettlementType.TOWN.value,
                    SettlementType.CITY.value,
                ]
                if i == 0:  # First usually major
                    settlement_type = SettlementType.CITY.value
                else:
                    settlement_type = random.choice(settlement_types)

                population = self._get_settlement_population(settlement_type, params)

                settlement = SettlementNode(
                    world_id=self.generated_world.id,
                    continent_id=region.continent_id,
                    empire_id=region.empire_id,
                    kingdom_id=region.kingdom_id,
                    region_id=region.id,
                    name=self._generate_settlement_name(),
                    settlement_type=settlement_type,
                    population=population,
                    location={"x": random.uniform(0, 1000), "y": random.uniform(0, 1000)},
                )

                self.persistence_service.create_settlement(settlement)
                region.settlement_ids.append(settlement.id)
                self.generated_world.settlements.append(settlement.id)

                # Set capital settlement if it's the largest
                if i == 0:
                    region.settlement_ids[0] = settlement.id
                    # Get the kingdom and set it as capital
                    if region.kingdom_id:
                        kingdom = self.persistence_service.load_kingdom(region.kingdom_id)
                        if kingdom and not kingdom.capital_settlement_id:
                            kingdom.capital_settlement_id = settlement.id
                            self.persistence_service.update_kingdom(kingdom)

            # Update region in persistence
            self.persistence_service.update_region(region)

    def _generate_routes(self, params: WorldGenerationParams) -> None:
        """Generate trade routes and connections between settlements."""
        if not self.generated_world:
            return

        settlements = self.persistence_service.list_settlements(self.generated_world.id)

        # For each region, connect settlements
        regions = self.persistence_service.list_regions(self.generated_world.id)

        for region in regions:
            region_settlements = [s for s in settlements if s.region_id == region.id]

            # Connect settlements within region
            for i in range(len(region_settlements) - 1):
                src = region_settlements[i]
                dst = region_settlements[i + 1]

                distance = ((src.location["x"] - dst.location["x"]) ** 2 + (src.location["y"] - dst.location["y"]) ** 2) ** 0.5

                route = Route(
                    source_id=src.id,
                    target_id=dst.id,
                    distance=distance,
                    route_type="trade_road",
                )

                self.persistence_service.create_route(route)
                src.connected_routes.append(route.id)
                dst.connected_routes.append(route.id)
                self.persistence_service.update_settlement(src)
                self.persistence_service.update_settlement(dst)

    def _generate_npcs(self, params: WorldGenerationParams) -> None:
        """Generate initial NPC populations for settlements."""
        if not self.generated_world:
            return

        settlements = self.persistence_service.list_settlements(self.generated_world.id)
        races = self.persistence_service.list_races()

        for settlement in settlements:
            # Calculate NPC population based on settlement size
            npc_count = max(2, int(settlement.population / 50 * params.get_npc_per_settlement_modifier()))

            for _ in range(npc_count):
                npc = NPC(
                    world_id=self.generated_world.id,
                    settlement_id=settlement.id,
                    name=self._generate_npc_name(),
                    age=random.randint(18, 80),
                    gender=random.choice(["Male", "Female"]),
                    occupation=random.choice([
                        "Merchant", "Guard", "Farmer", "Blacksmith", "Healer",
                        "Tavern Keeper", "Adventurer", "Scholar", "Priest", "Craftsperson",
                    ]),
                    health_status="Healthy",
                    fertility_score=random.uniform(0.2, 1.0) if _ % 3 != 0 else random.uniform(0.0, 0.3),
                )

                if races:
                    npc.race_id = random.choice(races).id

                self.persistence_service.create_npc(npc)
                if hasattr(settlement, 'npc_ids'):
                    settlement.npc_ids.append(npc.id)
                self.generated_world.npc_ids.append(npc.id)

            # Update settlement in persistence
            self.persistence_service.update_settlement(settlement)

    def _update_world_totals(self) -> None:
        """Update world with all generated entity counts."""
        if self.generated_world:
            self.persistence_service.update_world(self.generated_world)

    # Name generation helpers
    def _generate_continent_name(self, index: int) -> str:
        """Generate a continent name."""
        prefixes = ["Aurora", "Terra", "Mystral", "Valdor", "Ashnar", "Zephyr"]
        suffixes = ["ia", "ana", "eth", "orn", "ys", "ara"]
        return f"{prefixes[index % len(prefixes)]}{suffixes[index % len(suffixes)]}"

    def _generate_empire_name(self) -> str:
        """Generate an empire name."""
        names = [
            "Solarian", "Draconic", "Celestial", "Obsidian", "Chrystal",
            "Abyssal", "Radiant", "Twilight", "Emerald", "Crimson",
        ]
        return random.choice(names)

    def _generate_kingdom_name(self) -> str:
        """Generate a kingdom name."""
        names = [
            "Highmark", "Silverpine", "Goldholt", "Stoneheim", "Elmford",
            "Deephelm", "Ironvale", "Winterhold", "Sunmere", "Moonshadow",
        ]
        return random.choice(names)

    def _generate_region_name(self) -> str:
        """Generate a region name."""
        names = [
            "Northern Reaches", "Eastern Borderlands", "Western Peaks", "Southern Plains",
            "Central Valley", "Forest Lands", "Desert Wastes", "Mountain Spine",
        ]
        return random.choice(names)

    def _generate_settlement_name(self) -> str:
        """Generate a settlement name."""
        names = [
            "Westmarch", "Riverdale", "Haven", "Crossroads", "Bridge",
            "Market", "Port", "Grove", "Stone", "Wood", "Field", "Lake",
        ]
        suffixes = ["ford", "shire", "stone", "water", "gate", "hold", "town", "rest"]
        name = random.choice(names)
        suffix = random.choice(suffixes)
        return f"{name}{suffix}"

    def _generate_ruler_name(self) -> str:
        """Generate a ruler name."""
        first_names = ["Aldric", "Brennan", "Cedric", "Donovan", "Elric", "Garrett"]
        last_names = ["Thorne", "Storm", "Blackwood", "Ravenswood", "Ironheart"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _generate_npc_name(self) -> str:
        """Generate an NPC name."""
        first_names = [
            "Anna", "Bella", "Clara", "Diana", "Elara", "Fiona",
            "Aldous", "Brennus", "Cedric", "Dorian", "Ethan", "Fagan",
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez",
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _get_settlement_population(self, settlement_type: str, params: WorldGenerationParams) -> int:
        """Get base population for settlement type."""
        populations = {
            SettlementType.VILLAGE.value: (100, 500),
            SettlementType.TOWN.value: (500, 2000),
            SettlementType.CITY.value: (2000, 10000),
            SettlementType.CAPITAL.value: (5000, 20000),
        }

        min_pop, max_pop = populations.get(settlement_type, (100, 500))
        base_pop = random.randint(min_pop, max_pop)
        return max(100, int(base_pop * params.size_modifier))