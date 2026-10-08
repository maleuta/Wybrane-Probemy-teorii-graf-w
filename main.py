import os
import sys

# Zabezpieczenie przed błędami importów (dodanie katalogu głównego do sys.path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.parser import load_graph_from_json, load_grammar_from_json
from src.engine import GrammarEngine


def main():
    graph_path = os.path.join(BASE_DIR, "data", "initial_graph.json")
    grammar_path = os.path.join(BASE_DIR, "data", "grammar_spec.json")

    print(f"--> Ładowanie grafu: {graph_path}")
    graph = load_graph_from_json(graph_path)

    print(f"--> Ładowanie gramatyki: {grammar_path}")
    productions, policy = load_grammar_from_json(grammar_path)

    print("\n[Stan Początkowy]")
    print(graph)

    print("\n[Uruchomienie Maszyny Gramatyki]")
    engine = GrammarEngine(graph, productions, policy)
    engine.run()

    print("\n[Stan Końcowy]")
    print(graph)


if __name__ == "__main__":
    main()