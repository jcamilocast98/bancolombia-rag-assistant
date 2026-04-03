# ADR-001: Selección de Base Vectorial

## Estado
Aceptada

## Contexto
El sistema RAG necesita almacenar y buscar embeddings vectoriales de los chunks de documentos de Bancolombia Personas. Se requiere una base de datos que soporte:
- Búsqueda de similitud coseno eficiente
- Índices ANN (Approximate Nearest Neighbors)
- Integración con el ecosistema existente
- Bajo costo operacional

## Decisión
Usar **PostgreSQL + pgvector** como base de datos vectorial.

## Consecuencias

### Positivas
- Una sola base de datos para datos relacionales (historial, metadatos) y vectoriales
- Ecosistema maduro de PostgreSQL (backups, replicación, monitoring)
- Extensión open source sin costos de licencia
- Soporte para índices HNSW e IVFFlat
- Transacciones ACID para integridad de datos

### Negativas
- Rendimiento menor que soluciones especializadas (Qdrant, Milvus) para >10M vectores
- HNSW consume más memoria que IVFFlat
- No tiene sharding nativo para vectores

## Alternativas Evaluadas

| Alternativa | Razón de Descarte |
|------------|-------------------|
| Qdrant | Complejidad operacional adicional (servicio separado) |
| Pinecone | Vendor lock-in, costo recurrente |
| ChromaDB | No apto para producción, falta de SQL |
| Milvus | Over-engineered para el volumen esperado (<100K chunks) |
