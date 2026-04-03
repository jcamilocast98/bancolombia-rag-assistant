# 📜 Contratos de API entre Servicios

Este documento define los contratos de comunicación entre los servicios del sistema RAG.

---

## 1. Frontend → Agent API

### `POST /api/v1/chat`

**Request:**
```json
{
  "message": "¿Qué tipos de cuentas de ahorro ofrece Bancolombia?",
  "conversation_id": "uuid-opcional",
  "history": [
    {
      "role": "user",
      "content": "Hola",
      "timestamp": "2026-04-02T20:00:00Z"
    },
    {
      "role": "assistant",
      "content": "¡Hola! Soy el asistente virtual...",
      "timestamp": "2026-04-02T20:00:01Z"
    }
  ]
}
```

**Response (200):**
```json
{
  "response": "Bancolombia ofrece varios tipos de cuentas de ahorro:\n\n1. **Cuenta de Ahorros**...",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "sources": [
    {
      "title": "Cuenta de Ahorros - Bancolombia",
      "url": "https://www.bancolombia.com/personas/productos-servicios/cuentas/cuenta-de-ahorros",
      "snippet": "La Cuenta de Ahorros Bancolombia es un producto financiero que...",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "tokens_used": 1243,
    "response_time_ms": 2150
  }
}
```

**Response (500 - Error):**
```json
{
  "error": {
    "code": "LLM_TIMEOUT",
    "message": "El servicio de IA no respondió a tiempo. Por favor intente de nuevo.",
    "details": "Timeout after 30000ms"
  }
}
```

### `GET /api/v1/conversations/{conversation_id}`

**Response (200):**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [...],
  "created_at": "2026-04-02T20:00:00Z",
  "updated_at": "2026-04-02T20:05:00Z"
}
```

### `GET /health`

**Response (200):**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "mcp_server": "connected",
    "llm": "available"
  },
  "version": "0.1.0",
  "uptime_seconds": 3600
}
```

---

## 2. Agent → MCP Server (vía MCP Protocol)

### Tool: `search_knowledge_base`

**Input:**
```json
{
  "query": "cuentas de ahorro beneficios",
  "top_k": 5
}
```

**Output:**
```json
[
  {
    "chunk_id": "uuid",
    "content": "La Cuenta de Ahorros Bancolombia permite...",
    "url": "https://www.bancolombia.com/personas/...",
    "title": "Cuenta de Ahorros",
    "relevance_score": 0.92,
    "chunk_index": 3,
    "metadata": {
      "crawled_at": "2026-04-01T10:00:00Z"
    }
  }
]
```

### Tool: `get_article_by_url`

**Input:**
```json
{
  "url": "https://www.bancolombia.com/personas/productos-servicios/cuentas/cuenta-de-ahorros"
}
```

**Output:**
```json
{
  "url": "https://www.bancolombia.com/personas/...",
  "title": "Cuenta de Ahorros - Bancolombia",
  "content": "Contenido completo reconstruido de todos los chunks...",
  "total_chunks": 8,
  "last_updated": "2026-04-01T10:00:00Z"
}
```

### Resource: `knowledge-base://stats`

**Output:**
```json
{
  "total_documents": 342,
  "total_chunks": 4521,
  "last_updated": "2026-04-01T10:00:00Z",
  "embedding_model": "text-embedding-3-small",
  "embedding_dimensions": 1536,
  "avg_chunk_size_tokens": 487,
  "top_categories": [
    {"category": "cuentas", "count": 45},
    {"category": "tarjetas", "count": 38},
    {"category": "creditos", "count": 52}
  ]
}
```
