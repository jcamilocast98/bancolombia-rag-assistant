# 📐 Diagramas de Arquitectura C4

Esta carpeta contiene todos los diagramas de arquitectura del proyecto siguiendo el modelo C4:

## Niveles C4

| Nivel | Diagrama | Archivo | Descripción |
|-------|----------|---------|-------------|
| 1 | Contexto | `Diagrama de Contexto.webp` | Vista de alto nivel: usuario, sistema RAG, LLM, Bancolombia |
| 2 | Contenedores | `Diagra de Contenedores.webp` | Servicios: Frontend, Agent, MCP, Scraping, Indexador, DBs |
| 3 | Componentes (Completo) | `Diagra de Componentes Completos.webp` | Todos los componentes internos de cada contenedor |
| 3 | Componentes - Frontend | `Diagrama de componentes front end.webp` | Chat UI, Conversation History, Source Citation, API Client |
| 3 | Componentes - Agente | `Diagrama de componentes Agente.webp` | Agent Controller, LLM Orchestrator, Tool Dispatcher, Memory Manager, MCP Client |
| 3 | Componentes - MCP Server | `Diagrama de componentes MCP.webp` | MCP Server Core, Tools, Vector DB Accessor |
| 3 | Componentes - Web Scraping | `Diagrama Componente Web Scraping.webp` | Crawler/Explorer, Content Extractor, Queue, Storage Manager |
| 3 | Componentes - Indexador | `Diagrama de componentes Indexador.webp` | Data Cleaner, Indexador Orquestador, Text Chunker, Embedding Generator, Vector DB Accessor |

## Fuente Editable

- `Diagrama Arquitectura C4.drawio` — Archivo editable en [draw.io](https://app.diagrams.net/)

## Cómo Editar

1. Abrir [draw.io](https://app.diagrams.net/)
2. Cargar el archivo `.drawio`
3. Editar los diagramas
4. Exportar como `.webp` o `.png` para actualizar las imágenes
