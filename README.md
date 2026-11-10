# Architecture Copilot MCP 🧠🏗️

Un servidor MCP (Model Context Protocol) open source que analiza la arquitectura de tu proyecto usando `tree-sitter` y `networkx`. Construye un grafo de dependencias en tiempo real y permite a IAs (como GitHub Copilot o Cline) predecir y sugerir la estructura de nuevos módulos basándose en el código existente.

## 🚀 Características
- **Análisis estático:** Extrae clases, funciones e imports de tu código Python usando Tree-sitter.
- **Grafo de arquitectura:** Construye un grafo local con NetworkX.
- **Servidor MCP:** Expone herramientas para que los agentes de IA consulten la arquitectura del proyecto.

## 🛠️ Instalación y Uso
1. Clona este repositorio.
2. Sincroniza las dependencias: `uv sync`.
3. Genera el grafo de tu proyecto: 
   ```bash
   uv run python build_graph.py ./ruta-a-tu-proyectos