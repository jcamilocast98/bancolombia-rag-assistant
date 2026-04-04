import asyncio
import sys
import os

# Asegurar que el directorio src sea importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.dominio.entidades.crawl_job import CrawlJob
from src.infraestructura.adaptador_cola_redis import AdaptadorColaRedis

async def test_redis_integration():
    print("--- Iniciando prueba de Integración con Redis ---")
    
    # 1. Instanciar el adaptador
    try:
        cola = AdaptadorColaRedis()
        print(" [OK] Adaptador conectado a Redis correctamente.")
    except Exception as e:
        print(f" [ERROR] No se pudo conectar a Redis. ¿Está el contenedor corriendo? Error: {e}")
        return

    # 2. Preparar trabajos de prueba
    url_test = "https://www.bancolombia.com/test-redis"
    trabajo = CrawlJob(url=url_test, profundidad=1)

    # 3. Limpiar estado previo si existe (opcional para pureza del test)
    # cola.client.delete(cola.KEY_COLA, cola.KEY_VISITADAS)

    # 4. Probar encolado
    print(f" Encolando URL: {url_test}...")
    if cola.encolar(trabajo):
        print(" [OK] Trabajo encolado con éxito.")
    else:
        print(" [INFO] La URL ya estaba en la cola o visitada.")

    # 5. Probar visitadas
    print(" Marcando como visitada...")
    cola.marcar_como_visitada(url_test)
    if cola.ha_sido_visitada(url_test):
        print(" [OK] Marcado de visitadas funciona en Redis SET.")

    # 6. Probar desencolado (Persistencia)
    print(" Desencolando...")
    trabajo_recuperado = cola.desencolar()
    if trabajo_recuperado and trabajo_recuperado.url == url_test:
        print(f" [OK] Trabajo recuperado correctamente: {trabajo_recuperado.url} (Profundidad: {trabajo_recuperado.profundidad})")
    else:
        print(" [ERROR] La cola está vacía o el objeto es incorrecto.")

    print("--- Prueba finalizada ---")

if __name__ == "__main__":
    asyncio.run(test_redis_integration())
