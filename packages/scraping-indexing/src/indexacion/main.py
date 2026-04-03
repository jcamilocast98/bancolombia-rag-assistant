import asyncio
from datetime import datetime

from src.dominio.entidades.pagina import Pagina
from src.infraestructura.adaptador_almacenamiento_simulado import AdaptadorAlmacenamientoSimulado
from src.infraestructura.adaptador_embeddings_simulado import AdaptadorEmbeddingsSimulado
from src.infraestructura.adaptador_pgvector_simulado import AdaptadorPgVectorSimulado

from src.indexacion.limpiador_datos import LimpiadorDatos
from src.indexacion.segmentador_texto import SegmentadorTexto
from src.indexacion.generador_embeddings import GeneradorEmbeddings
from src.indexacion.acceso_bd_vectorial import AccesoBdVectorial
from src.indexacion.orquestador import OrquestadorIndexacion


async def main():
    print("[Tubería de Indexación] Inicializando...")

    # Adaptadores / Infraestructura Mock
    almacenamiento_mock = AdaptadorAlmacenamientoSimulado()
    embeddings_mock = AdaptadorEmbeddingsSimulado()
    bd_mock = AdaptadorPgVectorSimulado()

    # Creación de data cruda simulada en nuestro diccionario-Storage para probar el orquestador
    url_ejemplo = "https://www.bancolombia.com/personas/cuentas"
    html_ejemplo = "<html><body><nav>Menu Oculto</nav><main><h1>Cuentas de Ahorro</h1><p>Esta es la cuenta perfecta para ti. Sin cuota de manejo.</p></main><footer>Contacto</footer></body></html>"
    url_segura = url_ejemplo.replace("/", "_").replace(":", "_")
    ruta = f"{url_segura}.html"
    
    almacenamiento_mock._almacenamiento[ruta] = html_ejemplo

    # Componentes Principales
    limpiador = LimpiadorDatos()
    segmentador = SegmentadorTexto()
    gen_embeddings = GeneradorEmbeddings(puerto_embeddings=embeddings_mock)
    acc_bd = AccesoBdVectorial(puerto_bd=bd_mock)

    # El Orquestador
    orquestador = OrquestadorIndexacion(
        puerto_almacenamiento=almacenamiento_mock,
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
