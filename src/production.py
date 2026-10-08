from dataclasses import dataclass
from typing import Dict, List, Optional
from src.graph import Graph


@dataclass
class RuleEmbedding:
    left_vertex: int
    neighbor_label: str
    connect_to: List[int]


@dataclass
class NegativeCondition:
    left_vertex: int
    forbidden_label: str


class Production:
    def __init__(
        self,
        name: str,
        left: Graph,
        right: Graph,
        mapping: Dict[int, int],
        embeddings: List[RuleEmbedding],
        negative_conditions: Optional[List[NegativeCondition]] = None,
        priority: int = 1,
        dangling_edges: str = "delete"
    ):
        self.name = name
        self.left = left
        self.right = right
        self.mapping = mapping  # left_index -> right_index
        self.embeddings = embeddings
        self.negative_conditions = negative_conditions or []
        self.priority = priority
        self.dangling_edges = dangling_edges

    @classmethod
    def from_dict(cls, data: dict) -> "Production":
        left = Graph.from_dict(data["left"])
        right = Graph.from_dict(data["right"])

        mapping = {m["left"]: m["right"] for m in data.get("mapping", [])}

        embeddings = [
            RuleEmbedding(
                left_vertex=emb["leftVertex"],
                neighbor_label=emb["neighborLabel"],
                connect_to=emb["connectTo"]
            )
            for emb in data.get("embedding", [])
        ]

        neg_conditions = []
        for cond in data.get("negativeConditions", []):
            for item in cond.get("forbiddenNeighbors", []):
                neg_conditions.append(
                    NegativeCondition(
                        left_vertex=item["leftVertex"],
                        forbidden_label=item["neighborLabel"]
                    )
                )

        return cls(
            name=data.get("name", "P"),
            left=left,
            right=right,
            mapping=mapping,
            embeddings=embeddings,
            negative_conditions=neg_conditions,
            priority=data.get("priority", 1),
            dangling_edges=data.get("danglingEdges", "delete")
        )