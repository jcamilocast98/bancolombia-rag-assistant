# 🤖 Asistente Virtual RAG — Bancolombia

> **Sistema de Retrieval-Augmented Generation (RAG)** que permite a los usuarios consultar información de productos y servicios de Bancolombia Personas a través de un chat conversacional inteligente, respaldado por fuentes citables y verificables.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![Angular](https://img.shields.io/badge/Angular-17+-red?logo=angular&logoColor=white)](https://angular.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

---

## 📑 Tabla de Contenidos

- [Visión General](#visión-general)
- [Arquitectura y C4](#arquitectura-y-c4)
- [Comunicación SSE (Server-Sent Events)](#comunicación-sse-server-sent-events)
- [Endpoints y Swagger UI](#endpoints-y-swagger-ui)
- [Guía de Instalación (Docker)](#guía-de-instalación-docker)
- [Interactuando con el Agente (Uso de Herramientas MCP)](#interactuando-con-el-agente-uso-de-herramientas-mcp)
- [Decisiones de Arquitectura](#decisiones-de-arquitectura)
- [Testing y CI/CD](#testing-y-cicd)
- [Estructura del Monorepo](#estructura-del-monorepo)

---

## Visión General

Este asistente virtual implementa un flujo RAG robusto para el segmento **Personas** de Bancolombia:

1. **Ingesta**: Scraping ético de hasta 100 páginas del portal oficial "https://www.bancolombia.com/personas".
2. **Procesamiento**: Chunking semántico y generación de embeddings con `gemini-embedding-001`.
3. **Consulta**: Búsqueda vectorial en `pgvector` con scores de relevancia.
4. **Respuesta**: Orquestación con Gemini 2.5   y citación estricta de fuentes.

### Características Principales
- **Citas Verificables**: Cada respuesta incluye `(URL, Título, Relevancia)`.
- **Estadísticas en Vivo**: El agente puede informar sobre el volumen de su base de conocimiento.
- **Desacoplamiento MCP**: Herramientas de búsqueda separadas del core del agente.

---

## Arquitectura y C4

El proyecto sigue los principios de **Arquitectura Hexagonal** y **Clean Architecture**, dividiendo responsabilidades en capas de Dominio, Aplicación e Infraestructura.

### Diagramas de Arquitectura
Los diagramas detallados se encuentran en [documentation/diagramas/](file:///c:/Users/j-cam/repositorios/Prueba%20Banco/documentation/diagramas/):
- [**Nivel 1: Contexto**](file:///c:/Users/j-cam/repositorios/Prueba%20Banco/documentation/diagramas/Diagrama%20de%20Contexto.webp) - Visión global del sistema.
- [**Nivel 2: Contenedores**](file:///c:/Users/j-cam/repositorios/Prueba%20Banco/documentation/diagramas/Diagra%20de%20Contenedores.webp) - Interacción entre Apps y Bases de Datos.
- [**Nivel 3: Componentes**](file:///c:/Users/j-cam/repositorios/Prueba%20Banco/documentation/diagramas/Diagra%20de%20Componentes%20Completos.webp) - Detalle interno de cada microservicio.

---

## Comunicación SSE (Server-Sent Events)

Una decisión clave de diseño fue el uso de **SSE** para la comunicación entre el **Agente** y el **Servidor MCP**:

- **Bajo Acoplamiento**: El Agente no necesita conocer la implementación interna del servidor; solo consume las herramientas declaradas vía protocolo MCP.
- **Eficiencia sobre HTTP**: SSE permite una comunicación unidireccional de flujo constante que facilita la ejecución asíncrona de herramientas de larga duración (como búsquedas complejas o scraping en tiempo real).
- **Transporte**: Utilizamos el estándar de `mcp-sdk` sobre SSE para el intercambio seguro y tipado de mensajes JSON-RPC.

---

## Endpoints y Swagger UI

Al levantar el proyecto con Docker, los siguientes servicios quedan disponibles:

| Servicio | URL | Documentación (Swagger) |
|----------|-----|-------------------------|
| **Frontend UI** | [http://localhost:4200](http://localhost:4200) | N/A |
| **Agent API** | [http://localhost:8000](http://localhost:8000) | [/docs](http://localhost:8000/docs) |
| **MCP Server** | [http://localhost:8001](http://localhost:8001) | [/docs](http://localhost:8001/docs) |
| **MinIO Console**| [http://localhost:9001](http://localhost:9001) | N/A |
| **pgAdmin** | [http://localhost:5050](http://localhost:5050) | N/A |

---

## Guía de Instalación (Docker)

La forma más rápida de ejecutar el proyecto completo es mediante Docker Compose.

### 1. Requisitos
- Docker 24+ y Docker Compose 2.20+.
- API Key de Gemini (Google AI Studio).

### 2. Configuración
Crea un archivo `.env` en la carpeta `infrastructure/` basándote en el archivo `.env.example`:
```bash
cp infrastructure/.env.example infrastructure/.env
# Edita las variables, especialmente GEMINI_API_KEY
```

### 3. Ejecución
```bash
# Desde la raíz del proyecto
docker-compose -f infrastructure/docker-compose.yml up -d --build
```

---

## Interactuando con el Agente (Uso de Herramientas MCP)

El asistente orquestado con Gemini utiliza el **Model Context Protocol (MCP)** para decidir qué herramienta ejecutar basándose en la intención de tu pregunta. Aquí tienes ejemplos de cómo activarlas:

| Acción Deseada | Ejemplo de Consulta (Prompt) | Herramienta Ejecutada |
|----------------|------------------------------|-----------------------|
| **Búsqueda Semántica** | "¿Cuáles son los requisitos para un crédito de vehículo?" | `search_knowledge_base` |
| **Estadísticas del Sistema** | "¿Cuántos documentos tienes indexados y qué modelo usas?" | `get_knowledge_base_stats` |
| **Explorar Temas** | "¿Qué información tienes disponible?" o "¿De qué podemos hablar?" | `list_categories` |
| **Detalle de Artículo** | "Léeme el contenido completo de esta URL: [URL]" | `get_article_by_url` |

---

## Decisiones de Arquitectura

### 1. IA & Embeddings: Google Gemini
Se seleccionó la familia **Gemini** por su ventana de contexto masiva y el modelo de embeddings `gemini-embedding-001`, que ofrece un rendimiento superior en español y una latencia reducida comparado con otros proveedores.

### 2. Protocolo de Herramientas: MCP
El uso de **Model Context Protocol** permite que el Agente sea agnóstico a las herramientas. Si mañana necesitamos añadir una herramienta de "Consulta de Saldo", solo la añadimos al `mcp-server` y el Agente la descubrirá dinámicamente sin cambios en su código core.

### 3. Citación Estricta
Se implementó un sistema de **One-Shot Prompting** que obliga al LLM a seguir el formato:
`Fuentes: * (URL, Título, Score de Relevancia)`
Esto garantiza que el usuario siempre sepa de dónde proviene la información de Bancolombia.

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
│   │   ├── Dockerfile
│   │   └── angular.json
│   │
│   ├── 📂 agent/                  # Python — Cliente MCP / Orquestador LLM
│   │   ├── src/
│   │   │   ├── domain/            # Entidades, value objects, puertos (interfaces)
│   │   │   ├── application/       # Casos de uso, servicios de aplicación
│   │   │   ├── infrastructure/    # Adaptadores (Gemini, MCP, DB)
│   │   │   └── interfaces/       # Controladores FastAPI (API layer)
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   └── 📂 mcp-server/            # Python/FastAPI — Servidor MCP
│       ├── src/
│       │   ├── domain/            # Entidades de dominio, puertos
│       │   ├── application/       # Casos de uso (search, retrieve, stats)
│       │   ├── infrastructure/    # Adaptadores (pgvector, MCP SDK)
│       │   └── interfaces/       # MCP tools & resources exposure
│       ├── tests/
│       └── Dockerfile
│
├── 📂 packages/
│   └── 📂 scraping-indexing/      # Módulos de Crawling + Indexación
│       ├── src/
│       │   ├── scraping/          # Crawler, Extractor de Contenido
│       │   ├── indexing/          # Limpieza, Chunking, Generación de Embeddings
│       │   └── infrastructure/   # Adaptadores (Postgres, S3/MinIO)
│       └── tests/
│
├── 📂 infrastructure/
│   ├── docker-compose.yml         # Orquestación de todos los servicios
│   ├── .env.example               # Template de variables de entorno
│   └── 📂 ci-cd/
│
├── 📂 documentation/
│   ├── 📂 diagramas/              # Diagramas de arquitectura C4
│   └── 📂 decisiones/             # ADRs (Architecture Decision Records)
│
├── README.md                      # Este archivo
└── LICENSE
```

---

## Testing y CI/CD

El repositorio cuenta con un pipeline de integración continua robusto en GitHub Actions con **4 jobs en paralelo**:

1. **Scraping-Indexing**: Valida la lógica de extracción y limpieza de datos.
2. **Agent API**: Ejecuta pruebas de humo sobre los endpoints del orquestador.
3. **MCP Server**: Valida la disponibilidad de herramientas y recursos de la base de conocimiento.
4. **Angular Frontend**: Realiza una comprobación de construcción (`build`) para asegurar que no hay errores de sintaxis o tipos.

### 🔄 Pipeline de Extracción Automática (Cron)
Además del CI, existe el workflow `scraping_cron.yml` que:
- Se ejecuta semanalmente para mantener la base de conocimiento fresca.
- Utiliza **Service Containers** de GitHub para levantar instancias efímeras de **Redis** y **PostgreSQL (pgvector)**.
- Requiere el **Secret** `GEMINI_API_KEY` para generar los embeddings durante la fase de indexación.

---

<p align="center">
  <em>Desarrollado como solución técnica de alta disponibilidad para Proceso de Selección 59034 Bancolombia.</em>
</p>
