"""
knowledge_graph.py — In-memory directed graph the Kernel AI reasons over
directly. A real deployment backs this with 006_REALITY_GRAPH (temporal,
trust-scored graph store); this in-memory version is functionally complete
for a single node and used for the Foundation/Kernel prototype stage.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple


@dataclass
class Node:
    id: str
    kind: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    from_id: str
    to_id: str
    rel_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []

    def add_node(self, node: Node) -> None:
        self._nodes[node.id] = node

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def add_edge(self, edge: Edge) -> None:
        if edge.from_id not in self._nodes or edge.to_id not in self._nodes:
            raise KeyError("both endpoints must exist as nodes before adding an edge")
        self._edges.append(edge)

    def neighbors(self, node_id: str, rel_type: str | None = None) -> List[Node]:
        out = []
        for e in self._edges:
            if e.from_id == node_id and (rel_type is None or e.rel_type == rel_type):
                node = self._nodes.get(e.to_id)
                if node:
                    out.append(node)
        return out

    def query_by_kind(self, kind: str) -> List[Node]:
        return [n for n in self._nodes.values() if n.kind == kind]

    def edges_of(self, node_id: str) -> List[Edge]:
        return [e for e in self._edges if e.from_id == node_id or e.to_id == node_id]

    def shortest_path(self, start_id: str, goal_id: str) -> List[str] | None:
        """Unweighted BFS shortest path — enough for reasoning over small
        subgraphs; large-scale traversal belongs to 006_REALITY_GRAPH."""
        if start_id not in self._nodes or goal_id not in self._nodes:
            return None
        visited: Set[str] = {start_id}
        queue: List[Tuple[str, List[str]]] = [(start_id, [start_id])]
        while queue:
            current, path = queue.pop(0)
            if current == goal_id:
                return path
            for e in self._edges:
                if e.from_id == current and e.to_id not in visited:
                    visited.add(e.to_id)
                    queue.append((e.to_id, path + [e.to_id]))
        return None
