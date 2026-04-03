# 🤖 Asistente Virtual RAG — Bancolombia

> **Sistema de Retrieval-Augmented Generation (RAG)** que permite a los usuarios consultar información de productos y servicios de Bancolombia Personas a través de un chat conversacional inteligente, respaldado por fuentes citables y verificables.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![Angular](https://img.shields.io/badge/Angular-17+-red?logo=angular&logoColor=white)](https://angular.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📑 Tabla de Contenidos

- [Visión General](#visión-general)
- [Arquitectura](#arquitectura)
- [Estructura del Monorepo](#estructura-del-monorepo)
- [Requisitos Previos](#requisitos-previos)
- [Guía de Instalación](#guía-de-instalación)
- [Decisiones Técnicas Justificadas](#decisiones-técnicas-justificadas)
- [Herramientas MCP Obligatorias](#herramientas-mcp-obligatorias)
- [Variables de Entorno](#variables-de-entorno)
- [Testing](#testing)
- [Limitaciones Conocidas](#limitaciones-conocidas)
- [Mejoras Futuras](#mejoras-futuras)
- [Contribución](#contribución)

---

## Visión General

Este proyecto implementa un **Asistente Virtual Inteligente** basado en la arquitectura RAG (Retrieval-Augmented Generation) que:

1. **Crawlea** el sitio web `bancolombia.com/personas` de forma ética (respetando `robots.txt`).
2. **Limpia y segmenta** el contenido HTML en chunks semánticos optimizados.
3. **Genera embeddings** vectoriales y los almacena en una base de datos vectorial (pgvector).
4. **Expone herramientas MCP** (`search_knowledge_base`, `get_article_by_url`, `knowledge-base://stats`) para que el agente consulte la base de conocimiento.
5. **Orquesta un LLM** que responde preguntas del usuario con citación de fuentes verificables.
6. **Presenta las respuestas** en una interfaz de chat Angular con historial de conversación y enlaces a fuentes.

### Principios de Diseño

- **Arquitectura Hexagonal / Puertos y Adaptadores**: Cada servicio separa dominio, aplicación e infraestructura.
- **Inversión de Dependencias**: Las capas internas no dependen de las externas; se usan interfaces/puertos.
- **Bajo Acoplamiento**: Los servicios se comunican a través de contratos bien definidos (MCP Protocol, REST API).
- **Tolerancia a Fallos**: Circuit breakers, reintentos y manejo graceful de errores en cada capa.

---

## Arquitectura

### Diagrama de Contexto (C4 - Nivel 1)

```
┌─────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│   Usuario   │──────▶│  Agente de IA (RAG)  │──────▶│ sitio web        │
│             │       │  Sistema de Software  │       │ Bancolombia      │
└─────────────┘       └──────────┬───────────┘       └──────────────────┘
                                 │
                                 ▼
                      ┌──────────────────┐
                      │       LLM        │
                      │ (Sistema Externo)│
                      └──────────────────┘
```

### Diagrama de Contenedores (C4 - Nivel 2)

> 📌 Ver diagrama completo en `documentation/diagramas/`

```
┌────────────────────────────────────────────────────────────────────┐
│                        SISTEMA RAG BANCOLOMBIA                     │
│                                                                    │
│  ┌──────────┐   ┌─────────────┐   ┌──────────┐   ┌─────────────┐ │
│  │ Frontend │──▶│ API Gateway │──▶│  Agente  │──▶│ Web Scraping│ │
│  │ (Angular)│   │             │   │ (Python) │   │             │ │
│  └──────────┘   └─────────────┘   └────┬─────┘   └──────┬──────┘ │
│                                        │                  │        │
│                                        ▼                  ▼        │
│                              ┌──────────────┐    ┌──────────────┐  │
│                              │  MCP Server  │    │  Indexador   │  │
│                              │  (FastAPI)   │    │(Python+LC)   │  │
│                              └──────┬───────┘    └──────┬───────┘  │
│                                     │                    │         │
│                                     ▼                    ▼         │
│                              ┌─────────────────────────────────┐   │
│                              │   Base de Datos Vectorial       │   │
│                              │        (pgvector)               │   │
│                              └─────────────────────────────────┘   │
│                                                                    │
│  ┌─────────────────┐  ┌────────┐  ┌──────────┐                    │
│  │ BD Histórico    │  │ Colas  │  │ Storage  │                    │
│  │ (Conversaciones)│  │(Queue) │  │ (S3/Blob)│                    │
│  └─────────────────┘  └────────┘  └──────────┘                    │
└────────────────────────────────────────────────────────────────────┘
```

### Diagrama de Componentes (C4 - Nivel 3)

> 📐 Diagramas detallados por contenedor disponibles en `documentation/diagramas/`:
> - `Diagrama de Contexto.webp`
> - `Diagrama de Contenedores.webp`
> - `Diagrama de Componentes Completos.webp`
> - `Diagrama de componentes front end.webp`
> - `Diagrama de componentes Agente.webp`
> - `Diagrama de componentes MCP.webp`
> - `Diagrama Componente Web Scraping.webp`
> - `Diagrama de componentes Indexador.webp`

---

## Estructura del Monorepo

```
📦 bancolombia-rag-assistant/
├── 📂 apps/
│   ├── 📂 frontend/              # Angular 17+ — Interfaz de Chat
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── core/          # Servicios singleton, interceptors, guards
│   │   │   │   ├── features/      # Módulos de funcionalidad (chat, history)
│   │   │   │   ├── shared/        # Componentes reutilizables, pipes, directives
│   │   │   │   └── domain/        # Interfaces, modelos de dominio
│   │   │   ├── assets/
│   │   │   └── environments/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── angular.json
│   │
│   ├── 📂 agent/                  # Python — Cliente MCP / Orquestador LLM
│   │   ├── src/
│   │   │   ├── domain/            # Entidades, value objects, puertos (interfaces)
│   │   │   ├── application/       # Casos de uso, servicios de aplicación
│   │   │   ├── infrastructure/    # Adaptadores (LLM, MCP client, DB)
│   │   │   └── interfaces/       # Controladores FastAPI (API layer)
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── 📂 mcp-server/            # Python/FastAPI — Servidor MCP
│       ├── src/
│       │   ├── domain/            # Entidades de dominio, puertos
│       │   ├── application/       # Casos de uso (search, retrieve)
│       │   ├── infrastructure/    # Adaptadores (pgvector, MCP SDK)
│       │   └── interfaces/       # MCP tools & resources exposure
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── 📂 packages/
│   └── 📂 scraping-indexing/      # Módulos de Crawling + Indexación
│       ├── src/
│       │   ├── scraping/          # Crawler, Content Extractor, Storage Manager
│       │   ├── indexing/          # Data Cleaner, Text Chunker, Embedding Generator
│       │   ├── domain/            # Modelos compartidos
│       │   └── infrastructure/   # Adaptadores (Queue, S3, pgvector)
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── 📂 infrastructure/
│   ├── docker-compose.yml         # Orquestación de todos los servicios
│   ├── docker-compose.dev.yml     # Override para desarrollo local
│   ├── .env.example               # Template de variables de entorno
│   └── 📂 ci-cd/
│       └── 📂 .github/
│           └── 📂 workflows/
│               ├── ci.yml         # Pipeline de CI (lint, test, build)
│               └── cd.yml         # Pipeline de CD (deploy)
│
├── 📂 documentation/
│   ├── 📂 diagramas/              # Diagramas de arquitectura C4
│   ├── 📂 decisiones/             # ADRs (Architecture Decision Records)
│   ├── 📂 video-demo/             # Video demostración del proyecto
│   └── api-contracts.md           # Contratos de API entre servicios
│
├── README.md                      # Este archivo
├── .gitignore
└── LICENSE
```

---

## Requisitos Previos

| Herramienta      | Versión Mínima | Propósito                         |
|-----------------|----------------|-----------------------------------|
| Docker          | 24.0+          | Contenedores                      |
| Docker Compose  | 2.20+          | Orquestación                      |
| Node.js         | 18.x+          | Frontend Angular (dev)            |
| Python          | 3.11+          | Backend services (dev)            |
| Git             | 2.30+          | Control de versiones              |

---

## Guía de Instalación

### 🚀 Inicio Rápido (Docker Compose)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/bancolombia-rag-assistant.git
cd bancolombia-rag-assistant

# 2. Copiar y configurar variables de entorno
cp infrastructure/.env.example infrastructure/.env
# Editar infrastructure/.env con tus API keys

# 3. Levantar todos los servicios
docker-compose -f infrastructure/docker-compose.yml up --build

# 4. Acceder a la aplicación
# Frontend:    http://localhost:4200
# Agent API:   http://localhost:8000
# MCP Server:  http://localhost:8001
# pgAdmin:     http://localhost:5050
```

### 🛠️ Desarrollo Local (Sin Docker)

```bash
# Frontend
cd apps/frontend
npm install
ng serve

# Agent
cd apps/agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.interfaces.main:app --reload --port 8000

# MCP Server
cd apps/mcp-server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.interfaces.main:app --reload --port 8001

# Scraping & Indexing
cd packages/scraping-indexing
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.scraping.main  # Ejecutar crawler
python -m src.indexing.main  # Ejecutar indexación
```

---

## Decisiones Técnicas Justificadas

### 1. Modelo de Embeddings: `text-embedding-3-small` (OpenAI)

| Criterio              | Justificación                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| Dimensionalidad      | 1536 dims — balance entre precisión y rendimiento                             |
| Costo                | ~$0.02/1M tokens — económico para volúmenes moderados                        |
| Calidad              | MTEB benchmark top-tier para búsqueda semántica en español                   |
| Multilingüe          | Soporte nativo para español, crítico para contenido Bancolombia              |
| Alternativa evaluada | `all-MiniLM-L6-v2` (Sentence Transformers) — descartado por menor precisión en español |

### 2. Base Vectorial: PostgreSQL + pgvector

| Criterio         | Justificación                                                                 |
|-----------------|-------------------------------------------------------------------------------|
| Madurez         | Extensión oficial de PostgreSQL, ecosistema robusto                           |
| Simplicidad     | Una sola BD para datos relacionales + vectoriales (historial + embeddings)    |
| Rendimiento     | Índices HNSW/IVFFlat para búsqueda ANN eficiente                             |
| Costo           | Open source, sin licencia adicional                                           |
| Alternativa     | Qdrant, Pinecone — descartados por complejidad operacional adicional          |

### 3. Estrategia de Chunking: Recursive Character Text Splitter

| Criterio              | Justificación                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| Método               | Segmentación recursiva con separadores jerárquicos (`\n\n`, `\n`, `. `, ` `) |
| Tamaño de Chunk      | 512 tokens con overlap de 64 tokens                                           |
| Razón del tamaño     | Optimizado para ventana de contexto del LLM y granularidad de búsqueda        |
| Preservación semántica| El overlap asegura que no se pierda contexto en los bordes                    |
| Metadatos por chunk  | URL fuente, título de página, fecha de crawl, posición en documento            |

### 4. Protocolo de Comunicación: MCP (Model Context Protocol)

| Criterio         | Justificación                                                                 |
|-----------------|-------------------------------------------------------------------------------|
| Estándar         | Protocolo oficial de Anthropic para integración de herramientas con LLMs      |
| Transporte       | Soporte para stdio y SSE — flexibilidad en despliegue                         |
| Tipado           | Esquemas JSON tipados para tools y resources                                  |
| Extensibilidad   | Fácil adición de nuevas herramientas sin modificar el agente                 |

### 5. LLM: Claude 3.5 Sonnet (vía API Anthropic)

| Criterio         | Justificación                                                                 |
|-----------------|-------------------------------------------------------------------------------|
| Razonamiento     | Superior en tareas de síntesis y citación de fuentes                          |
| Tool Use         | Soporte nativo para function calling / tool use                               |
| Contexto         | 200K tokens — permite historial extenso de conversación                       |
| Costo            | Competitivo para volumen esperado de la prueba técnica                        |

---

## Herramientas MCP Obligatorias

### `search_knowledge_base`
```json
{
  "name": "search_knowledge_base",
  "description": "Busca en la base de conocimiento de Bancolombia Personas usando búsqueda semántica vectorial",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Consulta del usuario en lenguaje natural" },
      "top_k": { "type": "integer", "default": 5, "description": "Número de resultados a retornar" }
    },
    "required": ["query"]
  }
}
```

### `get_article_by_url`
```json
{
  "name": "get_article_by_url",
  "description": "Obtiene el contenido completo de un artículo dado su URL de Bancolombia",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "description": "URL del artículo en bancolombia.com" }
    },
    "required": ["url"]
  }
}
```

### `knowledge-base://stats` (Recurso MCP)
```json
{
  "uri": "knowledge-base://stats",
  "name": "Estadísticas de la Base de Conocimiento",
  "description": "Retorna métricas de la base de conocimiento: total de documentos, chunks, última actualización",
  "mimeType": "application/json"
}
```

---

## Variables de Entorno

Consultar `infrastructure/.env.example` para la lista completa. Variables críticas:

| Variable                   | Descripción                              | Requerida |
|---------------------------|------------------------------------------|-----------|
| `ANTHROPIC_API_KEY`       | API Key de Anthropic para Claude         | ✅        |
| `OPENAI_API_KEY`          | API Key de OpenAI para Embeddings        | ✅        |
| `POSTGRES_HOST`           | Host de PostgreSQL + pgvector            | ✅        |
| `POSTGRES_DB`             | Nombre de la base de datos               | ✅        |
| `POSTGRES_USER`           | Usuario de PostgreSQL                    | ✅        |
| `POSTGRES_PASSWORD`       | Contraseña de PostgreSQL                 | ✅        |
| `MCP_SERVER_URL`          | URL del servidor MCP                     | ✅        |
| `AGENT_API_PORT`          | Puerto del servicio Agent                | ⬜        |
| `FRONTEND_URL`            | URL del frontend (CORS)                  | ⬜        |

---

## Testing

```bash
# Tests unitarios del Agent
cd apps/agent && pytest tests/ -v --cov=src

# Tests unitarios del MCP Server
cd apps/mcp-server && pytest tests/ -v --cov=src

# Tests unitarios del Scraping/Indexing
cd packages/scraping-indexing && pytest tests/ -v --cov=src

# Tests del Frontend
cd apps/frontend && ng test --watch=false --code-coverage

# Tests de integración (requiere Docker)
docker-compose -f infrastructure/docker-compose.yml -f infrastructure/docker-compose.test.yml up --abort-on-container-exit
```

---

## Limitaciones Conocidas

| #  | Limitación                                    | Impacto                                            | Mitigación                                        |
|----|----------------------------------------------|----------------------------------------------------|----------------------------------------------------|
| 1  | Dependencia de APIs externas (LLM, Embeddings)| Latencia y costos variables                        | Caching de embeddings, rate limiting               |
| 2  | Crawling estático (no SPA/JS rendering)       | Contenido dinámico no capturado                    | Evaluar Playwright para rendering                  |
| 3  | Sin autenticación de usuarios                 | Historial compartido en sesión                     | Implementar JWT en fase 2                          |
| 4  | Base vectorial en un solo nodo                | Sin alta disponibilidad                            | Migrar a cluster PostgreSQL con réplicas           |
| 5  | Sin soporte offline                          | Requiere conectividad constante                    | Cache local de respuestas frecuentes               |
| 6  | Chunking uniforme                            | Puede fragmentar tablas o listas                   | Evaluar chunking semántico con Unstructured.io     |

---

## Mejoras Futuras

- [ ] 🔐 **Autenticación y Autorización**: Implementar OAuth2/JWT para sesiones de usuario
- [ ] 📊 **Dashboard de Observabilidad**: Integrar OpenTelemetry + Grafana para métricas del pipeline RAG
- [ ] 🔄 **Re-indexación Incremental**: Crawler programado con detección de cambios (delta crawling)
- [ ] 🌐 **Multi-idioma**: Soporte para inglés además de español
- [ ] 📱 **PWA**: Convertir el frontend en Progressive Web App
- [ ] 🧪 **Evaluación RAG**: Implementar métricas de RAGAS (Faithfulness, Relevancy, Context Recall)
- [ ] 💾 **Cache Semántico**: Cachear respuestas similares para reducir llamadas al LLM
- [ ] 🔍 **Hybrid Search**: Combinar búsqueda vectorial con BM25 (full-text) para mayor recall
- [ ] 📋 **Feedback Loop**: Permitir al usuario valorar respuestas para fine-tuning futuro

---

## Contribución

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/mi-feature`
3. Commit con convención: `git commit -m "feat(agent): agregar manejo de memoria"`
4. Push: `git push origin feature/mi-feature`
5. Crear Pull Request

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

<p align="center">
  <em>Desarrollado como prueba técnica — Asistente Virtual RAG para Bancolombia</em>
</p>
