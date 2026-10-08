import os
import matplotlib.pyplot as plt
import networkx as nx
from src.graph import Graph


def draw_graph(graph: Graph, title: str = "Wizualizacja Grafu", save_path: str = None, show: bool = True):
    """
    Rysuje graf za pomocą NetworkX i Matplotlib.
    Może wyświetlić okno (show=True) lub zapisać do pliku PNG (save_path).
    """
    # 1. Konwersja z Twojej klasy Graph na NetworkX
    G = nx.DiGraph() if graph.directed else nx.Graph()

    for idx, v in graph.vertices.items():
        G.add_node(idx, label=v.label)

    for u, neighbors in graph.adj.items():
        for v, edge in neighbors.items():
            if graph.directed or u <= v:
                G.add_edge(u, v, label=edge.label or "")

    # 2. Ustalenie układu (layout) wierzchołków na płaszczyźnie
    plt.figure(figsize=(7, 5))
    pos = nx.spring_layout(G, seed=42)

    # 3. Dynamiczne przypisanie kolorów na podstawie etykiet (A, X, Y, Z...)
    labels = [G.nodes[n]["label"] for n in G.nodes()]
    unique_labels = sorted(list(set(labels)))
    color_map = plt.cm.get_cmap("Set3", len(unique_labels))
    label_to_color = {lbl: color_map(i) for i, lbl in enumerate(unique_labels)}
    node_colors = [label_to_color[G.nodes[n]["label"]] for n in G.nodes()]

    # 4. Rysowanie węzłów i etykiet
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors="black", linewidths=1.5)
    
    # Etykieta wewnątrz węzła: np. "0:A"
    node_labels = {n: f"{n}:{G.nodes[n]['label']}" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=11, font_weight="bold")

    # 5. Rysowanie krawędzi
    nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.8, edge_color="gray")
    edge_labels = nx.get_edge_attributes(G, "label")
    edge_labels_filtered = {k: v for k, v in edge_labels.items() if v}
    if edge_labels_filtered:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_filtered, font_size=9)

    plt.title(title, fontsize=13, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()

    # 6. Zapis do pliku lub wyświetlenie
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"--> Zapisano obrazek: {save_path}")

    if show:
        plt.show()

    plt.close()