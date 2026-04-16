from __future__ import annotations

from typing import List

from app.core.services.persistence_service import PersistenceService
from app.domain.map.graph import MapEdge, MapNode, NodeGraph
from app.domain.models.structure import SettlementNode


class MapViewModel:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence_service = persistence_service

    def build_graph(self, world_id: str) -> NodeGraph:
        world_graph = NodeGraph()
        settlements = self.persistence_service.list_settlements(world_id)
        for settlement in settlements:
            node = MapNode(
                id=settlement.id,
                label=settlement.name,
                node_type=settlement.settlement_type,
                x=settlement.location.get("x", 0.0),
                y=settlement.location.get("y", 0.0),
                size=max(10.0, min(50.0, settlement.population / 20.0 + 10.0)),
                data={"population": settlement.population, "type": settlement.settlement_type},
            )
            world_graph.add_node(node)

        # Use connected_routes or neighbors if provided
        for settlement in settlements:
            for target_id in settlement.connected_routes:
                if target_id in world_graph.nodes:
                    edge = MapEdge(
                        id=f"{settlement.id}-{target_id}",
                        source=settlement.id,
                        target=target_id,
                        weight=1.0,
                    )
                    world_graph.add_edge(edge)

        return world_graph

    def available_worlds(self) -> List[str]:
        return [world.id for world in self.persistence_service.list_worlds()]
