from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Vertex:
    index: int
    label: str
    attributes: dict = field(default_factory=dict)


@dataclass
class Edge:
    u: int
    v: int
    label: Optional[str] = None
    weight: Optional[float] = None


class Graph:
    def __init__(self, name: str = "", directed: bool = False):
        self.name = name
        self.directed = directed
        self.vertices: Dict[int, Vertex] = {}
        # Lista sąsiedztwa: u -> {v: Edge}
        self.adj: Dict[int, Dict[int, Edge]] = {}

    def add_vertex(self, index: int, label: str, attributes: Optional[dict] = None) -> Vertex:
        vertex = Vertex(index=index, label=label, attributes=attributes or {})
        self.vertices[index] = vertex
        if index not in self.adj:
            self.adj[index] = {}
        return vertex

    def add_edge(self, u: int, v: int, label: Optional[str] = None, weight: Optional[float] = None):
        if u not in self.vertices or v not in self.vertices:
            raise ValueError(f"Wierzchołek {u} lub {v} nie istnieje w grafie '{self.name}'.")

        edge = Edge(u=u, v=v, label=label, weight=weight)
        self.adj[u][v] = edge
        if not self.directed:
            self.adj[v][u] = edge

    def remove_edge(self, u: int, v: int):
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
        if not self.directed and v in self.adj and u in self.adj[v]:
            del self.adj[v][u]

    def remove_vertex(self, index: int):
        if index not in self.vertices:
            return
        neighbors = list(self.adj[index].keys())
        for n in neighbors:
            self.remove_edge(index, n)
        del self.adj[index]
        del self.vertices[index]

    def get_neighbors(self, index: int) -> List[Tuple[Vertex, Edge]]:
        res = []
        for n_idx, edge in self.adj.get(index, {}).items():
            res.append((self.vertices[n_idx], edge))
        return res

    def get_next_available_index(self) -> int:
        return max(self.vertices.keys(), default=-1) + 1

    @classmethod
    def from_dict(cls, data: dict) -> "Graph":
        g = cls(name=data.get("name", ""), directed=data.get("directed", False))
        for v in data.get("vertices", []):
            g.add_vertex(v["index"], v["label"], v.get("attributes"))
        for e in data.get("edges", []):
            g.add_edge(e["u"], e["v"], e.get("label"), e.get("weight"))
        return g

    def __repr__(self) -> str:
        nodes_str = ", ".join(f"{v.index}:{v.label}" for v in self.vertices.values())
        edge_count = sum(len(x) for x in self.adj.values())
        if not self.directed:
            edge_count //= 2
        return f"Graph('{self.name}', |V|={len(self.vertices)}, |E|={edge_count}, Nodes=[{nodes_str}])"