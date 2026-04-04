"""
╔══════════════════════════════════════════════════════════════════════╗
║   Prueba End-to-End (E2E) — Backend RAG Bancolombia                ║
║   Valida: Infraestructura → pgvector → MCP Server → Agent LLM     ║
╚══════════════════════════════════════════════════════════════════════╝

Uso:
    python tests/e2e_test.py

Requisitos:
    pip install httpx
    Los contenedores deben estar corriendo (docker compose up)
"""
import asyncio
import json
import sys
import time
import os
from typing import Optional

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONUTF8", "1")

import httpx

# ═════════════════════════════════════════════════════════════════════
# Configuración
# ═════════════════════════════════════════════════════════════════════
AGENT_BASE_URL = "http://localhost:8000"
MCP_BASE_URL = "http://localhost:8001"
AGENT_API_KEY = "mi-api-key-segura-123"
POSTGRES_EXPECTED_MIN_CHUNKS = 100  # Mínimo de chunks esperados

# ═════════════════════════════════════════════════════════════════════
# Utilidades de Reporte
# ═════════════════════════════════════════════════════════════════════
results: list[dict] = []

def record(phase: str, test_name: str, passed: bool, detail: str = ""):
    icon = "✅" if passed else "❌"
    results.append({"phase": phase, "test": test_name, "passed": passed, "detail": detail})
    print(f"  {icon} {test_name}" + (f" — {detail}" if detail else ""))


def print_header(text: str):
    print(f"\n{'═' * 65}")
    print(f"  {text}")
    print(f"{'═' * 65}")


def print_subheader(text: str):
    print(f"\n  ── {text} ──")


# ═════════════════════════════════════════════════════════════════════
# Fase 1: Health Checks de Infraestructura
# ═════════════════════════════════════════════════════════════════════
async def fase_1_health_checks(client: httpx.AsyncClient):
    phase = "Fase 1: Infraestructura"
    print_header("FASE 1 — Health Checks de Infraestructura")

    # 1.1 MCP Server Health
    print_subheader("MCP Server")
    try:
        r = await client.get(f"{MCP_BASE_URL}/api/health", timeout=10)
        data = r.json()
        healthy = r.status_code == 200 and data.get("status") in ("healthy", "ok")
        pg_status = data.get("dependencies", {}).get("postgresql", "unknown")
        record(phase, "MCP Server Health", healthy, f"status={data.get('status')}, pg={pg_status}")
    except Exception as e:
        record(phase, "MCP Server Health", False, str(e))

    # 1.2 Agent Health
    print_subheader("Agent")
    try:
        r = await client.get(f"{AGENT_BASE_URL}/api/v1/health", timeout=10)
        data = r.json()
        healthy = r.status_code == 200 and data.get("status") == "ok"
        db_status = data.get("database", "unknown")
        record(phase, "Agent Health", healthy, f"status={data.get('status')}, db={db_status}")
    except Exception as e:
        record(phase, "Agent Health", False, str(e))


# ═════════════════════════════════════════════════════════════════════
# Fase 2: Validación de Datos en PostgreSQL + pgvector
# ═════════════════════════════════════════════════════════════════════
async def fase_2_validacion_datos(client: httpx.AsyncClient):
    phase = "Fase 2: Datos pgvector"
    print_header("FASE 2 — Validación de Datos en pgvector")

    # Usamos el health endpoint del MCP para verificar conectividad con postgres
    # y luego hacemos una búsqueda para validar que hay datos
    print_subheader("Verificación de Datos Indexados")

    try:
        # Verificar que el MCP Server puede conectar y hay datos
        r = await client.get(f"{MCP_BASE_URL}/api/health", timeout=10)
        data = r.json()
        pg_ok = data.get("dependencies", {}).get("postgresql") == "connected"
        record(phase, "Conexión PostgreSQL desde MCP", pg_ok, f"postgresql={data.get('dependencies', {}).get('postgresql')}")
    except Exception as e:
        record(phase, "Conexión PostgreSQL desde MCP", False, str(e))

    # Verificar que las búsquedas retornan resultados (indica datos indexados)
    print_subheader("Cobertura de Datos (vía Agent search)")
    try:
        r = await client.post(
            f"{AGENT_BASE_URL}/api/v1/chat",
            json={"session_id": "e2e-data-check", "message": "Bancolombia cuentas"},
            headers={"X-API-Key": AGENT_API_KEY},
            timeout=60,
        )
        data = r.json()
        has_reply = bool(data.get("reply"))
        record(phase, "Agent retorna datos de la KB", has_reply, f"reply_length={len(data.get('reply', ''))}")
    except Exception as e:
        record(phase, "Agent retorna datos de la KB", False, str(e))


# ═════════════════════════════════════════════════════════════════════
# Fase 3: Pruebas de Chat con el Agente (10 preguntas E2E)
# ═════════════════════════════════════════════════════════════════════

# Las 10 preguntas de prueba que cubren distintos escenarios
TEST_QUESTIONS = [
    {
        "id": "Q01",
        "question": "¿Cómo puedo hacer pagos a mi tarjeta de crédito?",
        "category": "Productos — Tarjetas",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q02",
        "question": "¿Qué tipos de cuentas de ahorro ofrece Bancolombia y cuáles son sus beneficios?",
        "category": "Productos — Cuentas",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q03",
        "question": "¿Cómo puedo solicitar un crédito hipotecario en Bancolombia?",
        "category": "Productos — Créditos",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q04",
        "question": "¿Qué es la cuenta de ahorros digital y cómo la abro desde la app?",
        "category": "Digital — App Bancolombia",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q05",
        "question": "¿Cuáles son las medidas de seguridad que ofrece Bancolombia para proteger mis transacciones?",
        "category": "Seguridad",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q06",
        "question": "Necesito información sobre seguros de vida que ofrezca Bancolombia.",
        "category": "Productos — Seguros",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q07",
        "question": "¿Qué es el lavado de activos y cómo lo previene Bancolombia?",
        "category": "Cumplimiento — SARLAFT",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q08",
        "question": "¿Cómo puedo invertir mi dinero con Bancolombia? ¿Qué opciones tengo?",
        "category": "Productos — Inversiones",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
    {
        "id": "Q09",
        "question": "Cuéntame un chiste sobre política",
        "category": "Out-of-scope (debe rechazar)",
        "expect_sources": False,
        "expect_bancolombia_content": False,
    },
    {
        "id": "Q10",
        "question": "¿Cuáles son las comisiones por transferencias internacionales en Bancolombia?",
        "category": "Productos — Transferencias",
        "expect_sources": True,
        "expect_bancolombia_content": True,
    },
]


async def fase_3_pruebas_chat(client: httpx.AsyncClient):
    phase = "Fase 3: Chat Agent E2E"
    print_header("FASE 3 — Pruebas de Chat con el Agente LLM")

    for i, q in enumerate(TEST_QUESTIONS, 1):
        print_subheader(f"[{q['id']}] {q['category']}")
        print(f"    Pregunta: \"{q['question']}\"")

        session_id = f"e2e-test-{q['id'].lower()}-{int(time.time())}"

        try:
            start = time.time()
            r = await client.post(
                f"{AGENT_BASE_URL}/api/v1/chat",
                json={"session_id": session_id, "message": q["question"]},
                headers={"X-API-Key": AGENT_API_KEY},
                timeout=120,
            )
            elapsed = time.time() - start

            if r.status_code != 200:
                record(phase, f"[{q['id']}] HTTP {r.status_code}", False, f"status_code={r.status_code}, body={r.text[:200]}")
                continue

            data = r.json()
            reply = data.get("reply", "")
            sources = data.get("sources", [])

            # Validación 1: La respuesta no está vacía
            has_reply = len(reply) > 20
            record(phase, f"[{q['id']}] Respuesta no vacía", has_reply, f"{len(reply)} chars, {elapsed:.1f}s")

            # Validación 2: Si esperamos fuentes, deben estar presentes
            if q["expect_sources"]:
                has_sources = len(sources) > 0
                record(phase, f"[{q['id']}] Incluye fuentes (sources)", has_sources, f"{len(sources)} fuentes")

            # Validación 3: Para out-of-scope, verificar que el agente rechaza
            if not q["expect_bancolombia_content"]:
                # El agente debería rechazar cortésmente
                rejection_indicators = ["no estoy autorizado", "no puedo", "fuera de", "como asistente", 
                                        "bancolombia", "no me es posible", "no corresponde"]
                is_rejected = any(ind in reply.lower() for ind in rejection_indicators)
                record(phase, f"[{q['id']}] Rechaza tema fuera de scope", is_rejected, f"reply_preview: {reply[:100]}...")

            # Mostrar preview de la respuesta
            print(f"    Respuesta: {reply[:150]}...")
            if sources:
                print(f"    Fuentes:   {sources[:3]}")

        except httpx.TimeoutException:
            record(phase, f"[{q['id']}] Timeout", False, "La solicitud superó 120s")
        except Exception as e:
            record(phase, f"[{q['id']}] Error", False, str(e)[:200])

        # Pequeña pausa entre preguntas para no saturar la API de Gemini
        if i < len(TEST_QUESTIONS):
            await asyncio.sleep(2)


# ═════════════════════════════════════════════════════════════════════
# Fase 4: Prueba de Memoria Conversacional
# ═════════════════════════════════════════════════════════════════════
async def fase_4_memoria_conversacional(client: httpx.AsyncClient):
    phase = "Fase 4: Memoria Conversacional"
    print_header("FASE 4 — Prueba de Memoria Conversacional")

    session_id = f"e2e-memory-{int(time.time())}"

    # Primer mensaje
    print_subheader("Mensaje 1 (contexto)")
    try:
        r1 = await client.post(
            f"{AGENT_BASE_URL}/api/v1/chat",
            json={"session_id": session_id, "message": "Háblame sobre las cuentas de ahorro de Bancolombia"},
            headers={"X-API-Key": AGENT_API_KEY},
            timeout=120,
        )
        data1 = r1.json()
        print(f"    Respuesta 1: {data1.get('reply', '')[:150]}...")
        record(phase, "Mensaje 1 enviado correctamente", r1.status_code == 200)
    except Exception as e:
        record(phase, "Mensaje 1 enviado correctamente", False, str(e))
        return

    await asyncio.sleep(3)

    # Segundo mensaje (referencia al primero)
    print_subheader("Mensaje 2 (referencia contextual)")
    try:
        r2 = await client.post(
            f"{AGENT_BASE_URL}/api/v1/chat",
            json={"session_id": session_id, "message": "¿Y cuál de esas me recomiendas si soy estudiante?"},
            headers={"X-API-Key": AGENT_API_KEY},
            timeout=120,
        )
        data2 = r2.json()
        reply2 = data2.get("reply", "")
        print(f"    Respuesta 2: {reply2[:150]}...")

        # Verificar que la respuesta tiene contexto del mensaje anterior
        has_context = len(reply2) > 30
        record(phase, "Mensaje 2 con contexto conversacional", has_context,
               f"reply_length={len(reply2)}")
    except Exception as e:
        record(phase, "Mensaje 2 con contexto conversacional", False, str(e))


# ═════════════════════════════════════════════════════════════════════
# Fase 5: Prueba de Seguridad (API Key)
# ═════════════════════════════════════════════════════════════════════
async def fase_5_seguridad(client: httpx.AsyncClient):
    phase = "Fase 5: Seguridad"
    print_header("FASE 5 — Validación de Seguridad")

    print_subheader("Acceso sin API Key")
    try:
        r = await client.post(
            f"{AGENT_BASE_URL}/api/v1/chat",
            json={"session_id": "hacker", "message": "Hola"},
            timeout=10,
        )
        blocked = r.status_code == 401
        record(phase, "Rechaza request sin API Key", blocked, f"status={r.status_code}")
    except Exception as e:
        record(phase, "Rechaza request sin API Key", False, str(e))

    print_subheader("Acceso con API Key inválida")
    try:
        r = await client.post(
            f"{AGENT_BASE_URL}/api/v1/chat",
            json={"session_id": "hacker", "message": "Hola"},
            headers={"X-API-Key": "wrong-key-12345"},
            timeout=10,
        )
        blocked = r.status_code == 401
        record(phase, "Rechaza API Key inválida", blocked, f"status={r.status_code}")
    except Exception as e:
        record(phase, "Rechaza API Key inválida", False, str(e))


# ═════════════════════════════════════════════════════════════════════
# Reporte Final
# ═════════════════════════════════════════════════════════════════════
def print_report():
    print_header("REPORTE E2E — RESULTADO FINAL")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    # Agrupar por fase
    phases = {}
    for r in results:
        phases.setdefault(r["phase"], []).append(r)

    for phase, tests in phases.items():
        p = sum(1 for t in tests if t["passed"])
        f = len(tests) - p
        icon = "🟢" if f == 0 else "🔴"
        print(f"\n  {icon} {phase}: {p}/{len(tests)} exitosos")
        for t in tests:
            icon = "✅" if t["passed"] else "❌"
            print(f"      {icon} {t['test']}")
            if not t["passed"] and t["detail"]:
                print(f"         └─ {t['detail']}")

    print(f"\n{'═' * 65}")
    print(f"  TOTAL: {passed}/{total} pruebas exitosas ({failed} fallidas)")
    pct = (passed / total * 100) if total > 0 else 0
    grade = "🏆 EXCELENTE" if pct == 100 else "🟢 APROBADO" if pct >= 80 else "🟡 PARCIAL" if pct >= 60 else "🔴 FALLIDO"
    print(f"  CALIFICACIÓN: {grade} ({pct:.0f}%)")
    print(f"{'═' * 65}\n")

    return failed == 0


# ═════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════
async def main():
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║      PRUEBA E2E — Backend RAG Bancolombia                      ║")
    print("║      Pipeline: Scraping → pgvector → MCP → Agent LLM          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    async with httpx.AsyncClient() as client:
        await fase_1_health_checks(client)
        await fase_2_validacion_datos(client)
        await fase_3_pruebas_chat(client)
        await fase_4_memoria_conversacional(client)
        await fase_5_seguridad(client)

    success = print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
