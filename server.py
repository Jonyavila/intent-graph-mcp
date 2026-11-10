"""Servidor MCP: Copiloto de Arquitectura basado en grafos."""
from pathlib import Path
import networkx as nx
from fastmcp import FastMCP

GRAPH_PATH = Path(__file__).parent / "grafo_proyecto.graphml"

if not GRAPH_PATH.exists():
    raise FileNotFoundError("No se encontró el grafo. Ejecuta primero: uv run python build_graph.py")

G = nx.read_graphml(GRAPH_PATH)
mcp = FastMCP("Architecture-Copilot")

@mcp.tool()
def search_similar_modules(intent: str) -> list[dict]:
    """Busca módulos del proyecto cuyo nombre se parezca a la intención del desarrollador."""
    keywords = [w.lower() for w in intent.split() if len(w) > 3]
    results = []
    for node, data in G.nodes(data=True):
        if data.get("type") != "module":
            continue
        score = sum(1 for kw in keywords if kw in node.lower())
        if score > 0:
            results.append({"module": node, "file": data.get("file"), "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]

@mcp.tool()
def get_module_template(module_name: str) -> dict:
    """Devuelve la estructura de un módulo del grafo."""
    if module_name not in G:
        return {"error": f"Módulo '{module_name}' no encontrado"}
    classes, functions, related = [], [], set()
    for neighbor in G.neighbors(module_name):
        data = G.nodes[neighbor]
        if data.get("type") == "class": classes.append(data.get("name"))
        elif data.get("type") == "function": functions.append(data.get("name"))
        elif data.get("type") == "module": related.add(data.get("file"))
    return {
        "module": module_name,
        "file": G.nodes[module_name].get("file"),
        "classes": classes,
        "functions": functions,
        "related_files": sorted(related),
    }

@mcp.tool()
def suggest_skeleton(intent: str) -> str:
    """Genera un esqueleto de módulo basado en la intención y el grafo."""
    similar = search_similar_modules(intent)
    if not similar:
        return f"No se encontraron módulos similares a '{intent}'."
    
    lines = [f"# Esqueleto propuesto para: {intent}", ""]
    lines.append("## Módulos de referencia detectados en el proyecto:")
    
    # Detectar qué lenguaje se está usando según el primer resultado
    first_file = similar[0]["file"]
    ext = Path(first_file).suffix if first_file else ".txt"
    
    for s in similar[:3]:
        t = get_module_template(s["module"])
        lines.append(f"\n### {t['module']} ({t['file']})")
        if t["classes"]: lines.append(f"  - Clases: {', '.join(t['classes'])}")
        if t["functions"]: lines.append(f"  - Funciones: {', '.join(t['functions'])}")
        if t["related_files"]: lines.append(f"  - Archivos relacionados: {', '.join(t['related_files'])}")
    
    # La IA leerá esto y sabrá qué extensión usar
    lines.append(f"\n## Estructura sugerida:")
    lines.append("Basado en el patrón detectado, crea los archivos necesarios siguiendo esta estructura.")
    lines.append(f"Extensión de archivo recomendada para este proyecto: {ext}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run()