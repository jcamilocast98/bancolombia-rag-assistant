import asyncio

from src.infraestructura.adaptador_cola_simulada import AdaptadorColaSimulada
from src.infraestructura.adaptador_almacenamiento_simulado import AdaptadorAlmacenamientoSimulado
from src.scraping.lector_robots import LectorRobots
from src.scraping.rastreador import Rastreador
from src.scraping.gestor_almacenamiento import GestorAlmacenamiento

async def main():
    print("[Tubería de Scraping] Inicializando...")
    
    # 1. Iniciar adaptadores
    cola = AdaptadorColaSimulada()
    almacenamiento = AdaptadorAlmacenamientoSimulado()
    
    # 2. Iniciar componentes
    lector_robots = LectorRobots()
    rastreador = Rastreador(puerto_cola=cola, lector_robots=lector_robots)
    gestor = GestorAlmacenamiento(puerto_almacenamiento=almacenamiento)

    # 3. Preparar la URL inicial
    await rastreador.iniciar_base()

    print("[Tubería de Scraping] Comenzando ciclo de rastreo...")
    continuar = True
    while continuar:
        
        async def descargar_y_guardar(url: str):
            # En un sistema real distribuido (Kafka, RabbitMQ, Celery), el crawler solo encola
            # y el downloader guarda asíncronamente; acá lo juntamos sincrónicamente por simplicidad
            ruta = await gestor.procesar_y_guardar(url)
            print(f"  [Almacenamiento] Guardado crudo: {url} -> {ruta}")
            # Retornar objeto Pagina para usar su contenido HTML
            return await gestor.extractor.descargar_pagina(url)

        continuar = await rastreador.procesar_trabajo(funcion_extraccion=descargar_y_guardar)
        
    print("[Tubería de Scraping] Finalizado exitosamente.")

if __name__ == "__main__":
    asyncio.run(main())
