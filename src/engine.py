import itertools
from typing import Dict, List, Optional
from src.graph import Graph
from src.production import Production


class GrammarEngine:
    def __init__(self, graph: Graph, productions: List[Production], execution_policy: dict):
        self.graph = graph
        self.productions = sorted(productions, key=lambda p: p.priority)
        self.policy = execution_policy

    # 1. SZUKANIE WZORCA (proste pętle zamiast rekurencji)
    def find_match(self, prod: Production) -> Optional[Dict[int, int]]:
        """Przeszukuje graf w poszukiwaniu podgrafu pasującego do prod.left."""
        left_indices = list(prod.left.vertices.keys())
        graph_indices = list(self.graph.vertices.keys())

        if len(left_indices) > len(graph_indices):
            return None

        # Sprawdzamy każdą kombinację wierzchołków w grafie
        for combo in itertools.permutations(graph_indices, len(left_indices)):
            match = dict(zip(left_indices, combo))

            # 1. Sprawdź etykiety węzłów
            labels_match = all(
                self.graph.vertices[g_id].label == prod.left.vertices[l_id].label
                for l_id, g_id in match.items()
            )
            if not labels_match:
                continue

            # 2. Sprawdź czy krawędzie z lewej strony istnieją w grafie
            edges_exist = all(
                match[v_l] in self.graph.adj.get(match[u_l], {})
                for u_l, neighbors in prod.left.adj.items()
                for v_l in neighbors
            )
            if not edges_exist:
                continue

            # 3. Sprawdź warunki negatywne (NAC)
            conflict = False
            for cond in prod.negative_conditions:
                g_node = match[cond.left_vertex]
                for neighbor, _ in self.graph.get_neighbors(g_node):
                    if neighbor.index not in match.values() and neighbor.label == cond.forbidden_label:
                        conflict = True
                        break
                if conflict:
                    break

            if not conflict:
                return match  # Znaleziono poprawne dopasowanie

        return None

    # 2. APLIKACJA PRODUKCJI (3 proste etapy)
    def apply_production(self, prod: Production, match: Dict[int, int]):
        matched_g_nodes = set(match.values())
        nodes_to_delete = [l_id for l_id in prod.left.vertices if l_id not in prod.mapping]

        # ETAP A: Zapisz krawędzie od usuwanych węzłów, a potem je skasuj
        dangling_edges = []
        for l_id in nodes_to_delete:
            g_id = match[l_id]
            for neighbor, edge in self.graph.get_neighbors(g_id):
                if neighbor.index not in matched_g_nodes:
                    dangling_edges.append((l_id, neighbor.index, neighbor.label, edge.label))
            self.graph.remove_vertex(g_id)

        # ETAP B: Dodaj prawą stronę do grafu (lub zaktualizuj zachowane)
        right_to_graph: Dict[int, int] = {}
        for r_id, r_vertex in prod.right.vertices.items():
            # Jeśli wierzchołek zachowany przez mapping
            left_id = next((l for l, r in prod.mapping.items() if r == r_id), None)
            if left_id is not None:
                g_id = match[left_id]
                self.graph.vertices[g_id].label = r_vertex.label
                right_to_graph[r_id] = g_id
            else:
                # Nowy wierzchołek
                new_id = self.graph.get_next_available_index()
                self.graph.add_vertex(new_id, r_vertex.label, r_vertex.attributes)
                right_to_graph[r_id] = new_id

        # Dodaj wewnętrzne krawędzie prawej strony
        for u_r, neighbors in prod.right.adj.items():
            for v_r, edge in neighbors.items():
                u_g, v_g = right_to_graph[u_r], right_to_graph[v_r]
                if v_g not in self.graph.adj.get(u_g, {}):
                    self.graph.add_edge(u_g, v_g, edge.label, edge.weight)

        # ETAP C: Przepnij urwane krawędzie (Embedding)
        for l_id, neighbor_g_id, neighbor_label, edge_label in dangling_edges:
            for rule in prod.embeddings:
                if rule.left_vertex == l_id and rule.neighbor_label in ("*", neighbor_label):
                    for target_r_id in rule.connect_to:
                        self.graph.add_edge(neighbor_g_id, right_to_graph[target_r_id], edge_label)

    # -------------------------------------------------------------
    # 3. GŁÓWNA PĘTLA
    # -------------------------------------------------------------
    def run(self):
        max_steps = self.policy.get("maxSteps", 50)

        for step in range(max_steps):
            applied = False
            for prod in self.productions:
                match = self.find_match(prod)
                if match:
                    print(f"Krok {step + 1}: Wykonano '{prod.name}' na wierzchołkach {match}")
                    self.apply_production(prod, match)
                    applied = True
                    break

            if not applied:
                print("Koniec: Brak pasujących produkcji.")
                break