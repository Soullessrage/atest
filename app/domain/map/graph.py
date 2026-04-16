from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MapNode:
    id: str
    label: str
    node_type: str
    x: float = 0.0
    y: float = 0.0
    size: float = 1.0
    data: Dict[str, object] = field(default_factory=dict)
    locked: bool = False


@dataclass
class MapEdge:
    id: str
    source: str
    target: str
    weight: float = 1.0
    route_type: str = "road"
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class NodeGraph:
    nodes: Dict[str, MapNode] = field(default_factory=dict)
    edges: Dict[str, MapEdge] = field(default_factory=dict)

    def add_node(self, node: MapNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: MapEdge) -> None:
        self.edges[edge.id] = edge

    def get_neighbors(self, node_id: str) -> List[MapNode]:
        return [self.nodes[edge.target] for edge in self.edges.values() if edge.source == node_id]
