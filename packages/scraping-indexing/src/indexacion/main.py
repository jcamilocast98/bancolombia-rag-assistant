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

    # Creación de data cruda simulada en MinIO para probar el orquestador
    url_ejemplo = "https://www.bancolombia.com/personas/cuentas"
    html_ejemplo = "<html><body><nav>Menu Oculto</nav><main><h1>Cuentas de Ahorro</h1><p>Esta es la cuenta perfecta para ti. Sin cuota de manejo.</p></main><footer>Contacto</footer></body></html>"
    
    pagina = Pagina(
        url=url_ejemplo,
        titulo="Cuentas Bancolombia",
        contenido_html=html_ejemplo,
        codigo_estado=200,
    )
    ruta = await almacenamiento.guardar_html_crudo(pagina)

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
    metadatos = {"titulo": "Cuentas Bancolombia Personas"}
    await orquestador.procesar_documento(
        ruta_almacenamiento=ruta, 
        url_origen=url_ejemplo, 
        metadatos=metadatos
    )
    
    print("[Tubería de Indexación] Proceso completado exitosamente.")

if __name__ == "__main__":
    asyncio.run(main())
