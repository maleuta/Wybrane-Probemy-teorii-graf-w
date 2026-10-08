import json
from typing import List, Tuple
from src.graph import Graph
from src.production import Production


def load_graph_from_json(filepath: str) -> Graph:
    """Wczytuje strukturę grafu z dedykowanego pliku JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Obsługuje zarówno przypadek, gdy klucz 'graph' jest na wierzchu, jak i bezpośredni obiekt
    graph_data = data.get("graph", data)
    return Graph.from_dict(graph_data)


def load_grammar_from_json(filepath: str) -> Tuple[List[Production], dict]:
    """Wczytuje reguły gramatyki oraz politykę wykonania."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    productions = [Production.from_dict(p) for p in data.get("productions", [])]
    policy = data.get("executionPolicy", {})
    return productions, policy