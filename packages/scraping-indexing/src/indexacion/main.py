import asyncio
from datetime import datetime

from src.dominio.entidades.pagina import Pagina
from src.infraestructura.adaptador_almacenamiento_s3 import AdaptadorAlmacenamientoS3
from src.infraestructura.adaptador_embeddings_simulado import AdaptadorEmbeddingsSimulado
from src.infraestructura.adaptador_pgvector import AdaptadorPgVector

from src.indexacion.limpiador_datos import LimpiadorDatos
from src.indexacion.segmentador_texto import SegmentadorTexto
from src.indexacion.generador_embeddings import GeneradorEmbeddings
from src.indexacion.acceso_bd_vectorial import AccesoBdVectorial
from src.indexacion.orquestador import OrquestadorIndexacion


async def main():
    print("[Tubería de Indexación] Inicializando...")

    # Adaptadores Reales
    almacenamiento = AdaptadorAlmacenamientoS3()
    embeddings = AdaptadorEmbeddingsSimulado()  # Cambiar por AdaptadorEmbeddingsOpenAI cuando haya API Key
    bd_vectorial = AdaptadorPgVector()

    # Creación de data cruda simulada en MinIO para probar el orquestador (Múltiples páginas para generar >10 chunks)
    paginas_prueba = [
        {
            "url": f"https://www.bancolombia.com/personas/test-{i}",
            "titulo": f"Página de Prueba {i}",
            "html": f"<html><body><main><h1>Sección {i} Bancolombia</h1><p>{'Información detallada de prueba para generar volumen de chunks. ' * 20}</p></main></body></html>"
        } for i in range(1, 11) # Generamos 10 páginas
    ]
    
    rutas = []
    for p in paginas_prueba:
        pagina = Pagina(
            url=p["url"],
            titulo=p["titulo"],
            contenido_html=p["html"],
            codigo_estado=200,
        )
        ruta = await almacenamiento.guardar_html_crudo(pagina)
        rutas.append((ruta, p["url"], {"titulo": p["titulo"]}))

    # Componentes Principales
    limpiador = LimpiadorDatos()
    segmentador = SegmentadorTexto()
    gen_embeddings = GeneradorEmbeddings(puerto_embeddings=embeddings)
    acc_bd = AccesoBdVectorial(puerto_bd=bd_vectorial)

    # El Orquestador
    orquestador = OrquestadorIndexacion(
        puerto_almacenamiento=almacenamiento,
        limpiador=limpiador,
        segmentador=segmentador,
        generador_embeddings=gen_embeddings,
        acceso_bd=acc_bd
    )

    print("[Tubería de Indexación] Corriendo flujo completo sobre los datos de prueba...")
    for r, u, m in rutas:
        await orquestador.procesar_documento(
            ruta_almacenamiento=r, 
            url_origen=u, 
            metadatos=m
        )
    
    print("[Tubería de Indexación] Proceso completado exitosamente.")

if __name__ == "__main__":
    asyncio.run(main())
