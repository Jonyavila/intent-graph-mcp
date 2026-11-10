# 🧠 Architecture Copilot MCP

<p align="center">
  <strong>Understand your architecture. Build smarter with AI.</strong>
</p>

<p align="center">
  An open-source MCP server that gives AI agents architectural awareness, deterministic scaffolding and project-specific coding rules.
</p>

---

**Architecture Copilot MCP** es una herramienta basada en **Model Context Protocol (MCP)** que permite a los agentes de IA comprender, consultar y respetar la arquitectura de un proyecto antes de generar código.

Utiliza `tree-sitter` y `networkx` para analizar el código fuente, construir un grafo de dependencias y extraer patrones arquitectónicos existentes.

A diferencia de los asistentes tradicionales que generan código basándose únicamente en instrucciones, Architecture Copilot incorpora una capa de contexto estructural que permite trabajar sobre las convenciones reales del proyecto.

Incluye tres capacidades fundamentales:

- **Architecture Intelligence:** comprensión de la estructura y los patrones existentes.
- **Deterministic Scaffolding:** creación física de carpetas y archivos siguiendo estructuras detectadas.
- **Architecture Guardrails:** reglas que orientan la generación de código y ayudan a mantener la consistencia arquitectónica.

## ✨ Características principales

- 🌐 **Análisis multi-lenguaje:** soporte para Python, JavaScript, TypeScript y TSX (React / Next.js).
- 🏗️ **Grafo arquitectónico:** representa las relaciones y dependencias entre módulos del proyecto.
- 🧹 **Filtrado inteligente:** ignora automáticamente directorios innecesarios como `node_modules`, `.next`, `.venv` y `dist`.
- 🤖 **Integración MCP:** permite que agentes como GitHub Copilot y Cline consulten la arquitectura mediante herramientas especializadas.
- 🧱 **Andamiaje determinista (`scaffold_module`):** crea físicamente carpetas y archivos basándose en estructuras existentes.
- 🚨 **Reglas arquitectónicas (`rules.json`):** permite definir convenciones y restricciones de diseño, como Clean Architecture.
- 🧠 **Contexto de generación (`get_generation_context`):** proporciona reglas y ejemplos del proyecto para orientar la generación de código.
- ⚡ **Procesamiento local:** analiza el código y construye el grafo localmente, sin depender de servicios externos para estas operaciones.

---

## 🛠️ Requisitos previos

### 1. Python y `uv`

Se utiliza [uv](https://docs.astral.sh/uv/) como gestor de dependencias y entornos de Python.

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Node.js (opcional)

Necesario únicamente si quieres utilizar el **MCP Inspector**, una interfaz visual para probar las herramientas del servidor.

Descárgalo desde [nodejs.org](https://nodejs.org/).

---

## ⚡ Instalación rápida

### Instalación global como herramienta de consola

La forma más rápida de utilizar Architecture Copilot MCP es instalar globalmente el comando de análisis mediante `uv`.

```bash
uv tool install git+https://github.com/Jonyavila/intent-graph-mcp.git
```

Una vez instalado, puedes analizar cualquier proyecto directamente desde la terminal.

**Windows**

```powershell
intent-graph "C:\Ruta\A\Tu\Proyecto"
```

**macOS / Linux**

```bash
intent-graph "./ruta-a-tu-proyecto"
```

### 📁 Ubicación del grafo arquitectónico

El análisis genera el archivo:

```text
grafo_proyecto.graphml
```

El archivo se almacena en el directorio de instalación de la herramienta, gestionado por `uv`, y no dentro de la carpeta del proyecto analizado.

Esto permite que el servidor MCP encuentre el grafo desde su propia ubicación.

> **Importante:** actualmente se utiliza un único grafo compartido. Cada nuevo análisis sobrescribe el anterior. Si trabajas con varios proyectos, debes volver a ejecutar `intent-graph` apuntando al proyecto que deseas analizar antes de utilizar la IA.

---

## 📦 Instalación para desarrollo

Si quieres modificar el código fuente o contribuir al proyecto:

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jonyavila/intent-graph-mcp.git

cd intent-graph-mcp
```

### 2. Instalar las dependencias

```bash
uv sync
```

### 3. Construir el grafo arquitectónico

Ejecuta el motor de análisis indicando la ruta del proyecto que quieres inspeccionar.

**Windows**

```powershell
uv run python build_graph.py "C:\Ruta\A\Tu\Proyecto"
```

**macOS / Linux**

```bash
uv run python build_graph.py "./ruta-a-tu-proyecto"
```

En esta modalidad, el grafo se genera en el directorio del repositorio clonado.

---

## 💻 Integración con VS Code

### Inicio automático del servidor MCP

Architecture Copilot MCP utiliza el transporte `stdio` para comunicarse con los asistentes de IA.

**No necesitas iniciar el servidor manualmente.**

VS Code se encarga de ejecutar `server.py` automáticamente en segundo plano cuando detecta la configuración MCP y se inicia el servidor desde el entorno correspondiente.

Crea o modifica el archivo:

```text
.vscode/mcp.json
```

Ubícalo en la raíz de tu proyecto y añade:

```json
{
  "servers": {
    "architecture-copilot": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "C:\\Users\\PC\\intent-graph-mcp",
        "python",
        "C:\\Users\\PC\\intent-graph-mcp\\server.py"
      ]
    }
  }
}
```

> **Importante:** reemplaza las rutas de ejemplo por la ubicación real donde clonaste el repositorio. En Windows utiliza barras invertidas dobles (`\\`) dentro del JSON.

### 🔄 Flujo de funcionamiento

1. Ejecutas `intent-graph` para analizar tu proyecto.
2. Se genera o actualiza `grafo_proyecto.graphml`.
3. Abres VS Code con la configuración MCP correspondiente.
4. VS Code inicia `server.py` automáticamente.
5. GitHub Copilot o Cline pueden utilizar las herramientas disponibles.

**Consideración:** el servidor lee el grafo almacenado en la carpeta del repositorio clonado. Por eso, el grafo generado mediante la instalación global y el utilizado por el servidor deben estar sincronizados. Actualmente, el último análisis reemplaza al anterior.

---

## 📜 Configuración de reglas arquitectónicas

Architecture Copilot permite definir convenciones mediante un archivo `rules.json`.

Puedes utilizarlo para establecer patrones de diseño y restricciones que el agente debe tener en cuenta durante la generación de código.

Crea el archivo en la ubicación que utiliza el servidor:

```text
rules.json
```

Ejemplo:

```json
{
  "patron": "Clean Architecture",
  "reglas": [
    "Los controladores NO pueden importar modelos de base de datos directamente.",
    "Los nombres de los archivos deben utilizar kebab-case.",
    "Todas las funciones asíncronas deben manejar sus propios errores."
  ]
}
```

Las reglas se incorporan al contexto de generación para orientar al agente de IA.

> Si no configuras `rules.json`, puedes seguir utilizando las herramientas de análisis y generación contextual con los patrones detectados en el grafo.

---

## 🎯 Ejemplos de uso con IA

Abre GitHub Copilot en modo **Agent** y utiliza los siguientes ejemplos para interactuar con el servidor.

### 1. 🧱 Andamiaje físico

**Herramienta:** `scaffold_module`

Crea primero la estructura física del módulo y después permite que la IA implemente su lógica.

**Prompt:**

```text
Utiliza scaffold_module con el intent "login-form"
y la ruta "D:\Ruta\A\Tu\Proyecto".

Crea físicamente las carpetas y archivos correspondientes.
Después, implementa la lógica dentro de los archivos creados,
respetando las reglas arquitectónicas del proyecto.
```

**Resultado esperado:** el servidor crea las carpetas y archivos correspondientes. La IA trabaja sobre esa estructura en lugar de inventar rutas.

### 2. 🚨 Generación con reglas arquitectónicas

**Herramienta:** `get_generation_context`

Obtiene el contexto de generación, incluyendo las reglas y los ejemplos disponibles.

**Prompt:**

```text
Utiliza get_generation_context para "payments".

Analiza el manual de estilo, las reglas arquitectónicas
y los ejemplos existentes.

Después, implementa el módulo de pagos respetando
las convenciones y la arquitectura del proyecto.
```

**Resultado esperado:** el agente recibe contexto arquitectónico para generar código coherente con las convenciones existentes.

### 3. 🔍 Exploración de módulos existentes

**Herramientas:** `search_similar_modules` y `get_module_template`

Permite consultar cómo están construidos los módulos antes de modificarlos o crear otros similares.

**Prompt:**

```text
Utiliza search_similar_modules para buscar "header".

Después, utiliza get_module_template para consultar
su estructura, funciones y archivos.

Explícame cómo está organizado y qué patrones
debería respetar al crear un componente similar.
```

**Resultado esperado:** el agente obtiene una referencia estructural de los módulos existentes.

---

## 🔄 ¿Qué sucede internamente?

Architecture Copilot MCP incorpora un flujo de trabajo que conecta el análisis del código con la generación asistida por IA.

1. **Análisis:** `tree-sitter` analiza los archivos y extrae información estructural.
2. **Representación:** `networkx` construye el grafo de dependencias.
3. **Consulta:** el agente utiliza las herramientas MCP para explorar módulos y patrones.
4. **Contextualización:** `get_generation_context` proporciona reglas y ejemplos.
5. **Andamiaje:** `scaffold_module` crea físicamente la estructura solicitada.
6. **Generación:** el agente implementa el código utilizando el contexto arquitectónico disponible.

---

## 🧰 Herramientas MCP disponibles

| Herramienta | Descripción |
|:---|:---|
| `search_similar_modules` | Busca módulos similares dentro del grafo según una intención. |
| `get_module_template` | Obtiene la estructura detallada de un módulo, incluyendo clases, funciones y archivos. |
| `suggest_skeleton` | Recomienda la estructura de un nuevo módulo a partir de patrones existentes. |
| `get_generation_context` | Devuelve el contexto de generación, incluyendo reglas y ejemplos del proyecto. |
| `scaffold_module` | Crea físicamente carpetas y archivos basándose en el grafo arquitectónico. |

---

## 🧱 Tecnologías utilizadas

| Tecnología | Función |
|:---|:---|
| **Python** | Motor de análisis y lógica del servidor. |
| **Tree-sitter** | Análisis sintáctico del código fuente. |
| **NetworkX** | Construcción y gestión del grafo de dependencias. |
| **MCP** | Comunicación entre el servidor y los agentes de IA. |
| **uv** | Gestión de dependencias y ejecución del proyecto. |
| **GraphML** | Formato de almacenamiento del grafo arquitectónico. |

---

## 🚀 Objetivo del proyecto

Architecture Copilot MCP busca mejorar la forma en que los agentes de IA interactúan con bases de código existentes.

Su propósito es incorporar una capa de inteligencia arquitectónica que permita generar código más coherente, respetar las convenciones del proyecto y reducir inconsistencias estructurales.

No se trata solamente de sugerir código: se trata de proporcionar a la IA una comprensión más profunda de cómo está construido el software y cómo debería evolucionar.

> **La IA no debería limitarse a escribir código. También debería comprender cómo está construido el proyecto.**

---

## 📄 Licencia

Este proyecto es open source. Consulta el archivo [LICENSE](LICENSE) para conocer los términos de uso y distribución.