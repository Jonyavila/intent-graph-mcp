"""Motor de construcción del grafo arquitectónico del proyecto."""
from pathlib import Path
import sys

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import networkx as nx

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def node_text(node, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")

def analyze_file(file_path: Path, repo_root: Path, G: nx.DiGraph) -> None:
    source = file_path.read_bytes()
    tree = parser.parse(source)
    rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
    module_id = f"module::{rel_path}"

    G.add_node(module_id, type="module", file=rel_path)

    def walk(node):
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    mod = node_text(child, source)
                    G.add_edge(module_id, f"module::{mod.replace('.', '/')}.py", type="imports")

        elif node.type == "import_from_statement":
            mod_node = node.child_by_field_name("module_name")
            if mod_node and mod_node.type == "dotted_name":
                mod = node_text(mod_node, source)
                G.add_edge(module_id, f"module::{mod.replace('.', '/')}.py", type="imports_from")

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                func_id = f"function::{rel_path}::{name}"
                G.add_node(func_id, type="function", name=name, file=rel_path)
                G.add_edge(module_id, func_id, type="contains")

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                class_id = f"class::{rel_path}::{name}"
                G.add_node(class_id, type="class", name=name, file=rel_path)
                G.add_edge(module_id, class_id, type="contains")

        for child in node.children:
            walk(child)

    walk(tree.root_node)

def main(repo_path_str: str) -> None:
    repo_root = Path(repo_path_str).resolve()
    if not repo_root.exists():
        sys.exit(f"No existe la ruta: {repo_root}")

    G = nx.DiGraph()
    files = list(repo_root.rglob("*.py"))
    if not files:
        sys.exit(f"No se encontraron archivos .py en {repo_root}")

    for py_file in files:
        analyze_file(py_file, repo_root, G)

    out = Path(__file__).parent / "grafo_proyecto.graphml"
    nx.write_graphml(G, out)
    print(f"OK -> {out}")
    print(f"   Nodos: {G.number_of_nodes()} | Aristas: {G.number_of_edges()}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./mi-proyecto-ejemplo"
    main(target)