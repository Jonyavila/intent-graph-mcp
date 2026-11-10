"""Motor de construcción del grafo arquitectónico multi-lenguaje."""
from pathlib import Path
import sys

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser
import networkx as nx

# Configurar los lenguajes
LANG_PYTHON = Language(tspython.language())
LANG_JS = Language(tsjavascript.language())
LANG_TS = Language(tstypescript.language_typescript())
LANG_TSX = Language(tstypescript.language_tsx())

# Mapeo de extensiones a lenguajes
LANGUAGES = {
    ".py": LANG_PYTHON,
    ".js": LANG_JS,
    ".jsx": LANG_JS,
    ".ts": LANG_TS,
    ".tsx": LANG_TSX,
}

# Carpetas que NUNCA debemos escanear (caché, builds, dependencias)
IGNORED_DIRS = {".venv", "node_modules", ".next", "dist", "build", ".git", "coverage", ".nuxt", "out"}

def is_ignored(path: Path, root: Path) -> bool:
    """Revisa si el archivo está dentro de una carpeta ignorada."""
    try:
        rel_parts = path.relative_to(root).parts
        return any(part in IGNORED_DIRS for part in rel_parts)
    except ValueError:
        return False

def node_text(node, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")

def analyze_file(file_path: Path, repo_root: Path, G: nx.DiGraph) -> None:
    ext = file_path.suffix.lower()
    if ext not in LANGUAGES:
        return

    source = file_path.read_bytes()
    parser = Parser(LANGUAGES[ext])
    tree = parser.parse(source)
    
    rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
    module_id = f"module::{rel_path}"

    G.add_node(module_id, type="module", file=rel_path, language=ext)

    def walk(node):
        if node.type in ("import_statement", "import_from_statement"):
            text = node_text(node, source)
            G.add_edge(module_id, text, type="imports", file=rel_path)
        elif node.type in ("class_definition", "class_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                class_id = f"class::{rel_path}::{name}"
                G.add_node(class_id, type="class", name=name, file=rel_path)
                G.add_edge(module_id, class_id, type="contains")
        elif node.type in ("function_definition", "function_declaration", "method_definition"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = node_text(name_node, source)
                func_id = f"function::{rel_path}::{name}"
                G.add_node(func_id, type="function", name=name, file=rel_path)
                G.add_edge(module_id, func_id, type="contains")
        for child in node.children:
            walk(child)

    walk(tree.root_node)

def main(repo_path_str: str) -> None:
    repo_root = Path(repo_path_str).resolve()
    if not repo_root.exists():
        sys.exit(f"❌ No existe la ruta: {repo_root}")

    G = nx.DiGraph()
    
    valid_exts = tuple(LANGUAGES.keys())
    files = []
    
    # Filtrar archivos ignorando carpetas de build
    for f in repo_root.rglob("*"):
        if f.is_file() and f.suffix.lower() in valid_exts and not is_ignored(f, repo_root):
            files.append(f)
    
    if not files:
        sys.exit(f"❌ No se encontraron archivos de código fuente en {repo_root}")

    for file in files:
        analyze_file(file, repo_root, G)

    out = Path(__file__).parent / "grafo_proyecto.graphml"
    nx.write_graphml(G, out)
    print(f"✅ Grafo generado en: {out}")
    print(f"   📊 Nodos: {G.number_of_nodes()} | Aristas: {G.number_of_edges()}")
    print(f"   📂 Archivos analizados: {len(files)}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./mi-proyecto-ejemplo"
    main(target)