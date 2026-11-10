"""Servidor MCP: Copiloto de Arquitectura basado en grafos."""
from pathlib import Path
import json
import networkx as nx
from fastmcp import FastMCP

GRAPH_PATH = Path(__file__).parent / "grafo_proyecto.graphml"
RULES_PATH = Path(__file__).parent / "rules.json"

if not GRAPH_PATH.exists():
    raise FileNotFoundError("No se encontró el grafo. Ejecuta: intent-graph <ruta>")

G = nx.read_graphml(GRAPH_PATH)
mcp = FastMCP("Architecture-Copilot")

def get_rules():
    """Carga las reglas si el archivo existe."""
    if RULES_PATH.exists():
        try:
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

@mcp.tool()
def search_similar_modules(intent: str) -> list[dict]:
    """Busca módulos del proyecto cuyo nombre se parezca a la intención."""
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
def get_generation_context(intent: str) -> str:
    """Devuelve el manual de estilo y las reglas para que la IA genere código."""
    similar = search_similar_modules(intent)
    rules = get_rules()
    
    context = [f"# Contexto de Generación para: {intent}", ""]
    
    if rules:
        context.append("## 🚨 REGLAS ESTRICTAS DE ARQUITECTURA (OBLIGATORIO CUMPLIR):")
        if "patron" in rules:
            context.append(f"- Patrón de diseño: **{rules['patron']}**")
        for regla in rules.get("reglas", []):
            context.append(f"- {regla}")
        context.append("")
    
    if similar:
        context.append("## 🏗️ Patrones detectados en el proyecto:")
        for s in similar[:2]:
            t = get_module_template(s["module"])
            context.append(f"- Archivo de referencia: `{t['file']}`")
            if t["classes"]: context.append(f"  - Clases: {', '.join(t['classes'])}")
    else:
        context.append("## 🏗️ Patrones: No se encontraron módulos similares. Usa las convenciones estándar del lenguaje.")
        
    return "\n".join(context)

@mcp.tool()
def scaffold_module(intent: str, target_project_path: str) -> str:
    """
    MODO ANDAMIAJE: Crea la estructura física de carpetas y archivos vacíos 
    basándose en el grafo, para que la IA solo rellene la lógica.
    """
    similar = search_similar_modules(intent)
    rules = get_rules()
    target_dir = Path(target_project_path)
    
    if not target_dir.exists():
        return f"Error: La ruta del proyecto {target_project_path} no existe."
        
    if not similar:
        return f"No se encontraron módulos similares a '{intent}'. No se puede inferir la estructura exacta."

    ref_module = similar[0]["module"]
    ref_file = G.nodes[ref_module].get("file")
    
    if not ref_file:
        return "No se pudo determinar la ruta del archivo de referencia."

    ref_path = Path(ref_file)
    parent_dir = ref_path.parent 
    new_dir_name = intent.lower().replace(" ", "-")
    new_parent_dir = parent_dir.parent / new_dir_name 
    
    ref_filename = ref_path.name
    ref_base_name = ref_path.stem 
    suffix = ref_filename.replace(ref_base_name.split('.')[0], "") 
    
    new_filename = f"{new_dir_name}{suffix}"
    
    final_dir = target_dir / new_parent_dir
    final_file = final_dir / new_filename
    
    try:
        final_dir.mkdir(parents=True, exist_ok=True)
        if not final_file.exists():
            final_file.touch()
            
        result = [f"✅ **Andamiaje creado exitosamente:**"]
        result.append(f"- Carpeta: `{final_dir}`")
        result.append(f"- Archivo: `{final_file}`")
        result.append(f"\n**INSTRUCCIÓN PARA LA IA:** He creado el archivo físico basándome en el patrón de `{ref_module}`. Ahora debes escribir la lógica dentro de `{new_filename}`.")
        
        if rules:
            result.append("\n## 🚨 REGLAS OBLIGATORIAS:")
            if "patron" in rules: result.append(f"- Patrón: {rules['patron']}")
            for r in rules.get("reglas", []): result.append(f"- {r}")
            
        return "\n".join(result)
        
    except Exception as e:
        return f"Error creando el andamiaje: {str(e)}"

if __name__ == "__main__":
    mcp.run()