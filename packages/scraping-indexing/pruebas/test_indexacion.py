import pytest
from src.indexacion.limpiador_datos import LimpiadorDatos
from src.indexacion.segmentador_texto import SegmentadorTexto
from src.indexacion.generador_embeddings import GeneradorEmbeddings
from src.infraestructura.adaptador_embeddings_simulado import AdaptadorEmbeddingsSimulado
from src.dominio.entidades.chunk import Chunk

# --- Pruebas Indexación ---

def test_limpiador_datos():
    limpiador = LimpiadorDatos()
    html_entrada = """
    <html>
        <head><title>Página de Prueba</title></head>
        <body>
            <nav><div>Enlace al Menú</div></nav>
            <main>
                <h1>Título Principal</h1>
                <p>Hola mundo.</p>
                <script>alert("prueba");</script>
            </main>
            <footer>Derechos Reservados 2024</footer>
        </body>
    </html>
    """
    texto = limpiador.limpiar_html(html_entrada)
    assert "Título Principal" in texto
    assert "Hola mundo." in texto
    assert "Enlace al Menú" not in texto
    assert "alert" not in texto
    assert "Derechos Reservados" not in texto


def test_segmentador_texto():
    segmentador = SegmentadorTexto()
    # Forzar un tamaño de chunk pequeño para validar la separación
    segmentador.separador._chunk_size = 50
    segmentador.separador._chunk_overlap = 10
    
    texto_largo = "Este es un texto muy largo diseñado para probar el segmentador de texto. " * 5
    url = "http://ejemplo.com"
    
    chunks = segmentador.segmentar_texto(url, texto_largo, {"titulo": "Prueba"})
    
    assert len(chunks) > 1
    assert chunks[0].url == url
    assert "titulo" in chunks[0].metadatos
    assert chunks[0].indice_chunk == 0
    assert chunks[1].indice_chunk == 1


@pytest.mark.asyncio
async def test_generador_embeddings():
    adaptador_mock = AdaptadorEmbeddingsSimulado()
    generador = GeneradorEmbeddings(adaptador_mock)
    
    chunks = [
        Chunk(id_chunk="1", url="http://ejemplo.com", contenido_texto="chunk 1", indice_chunk=0),
        Chunk(id_chunk="2", url="http://ejemplo.com", contenido_texto="chunk 2", indice_chunk=1),
    ]
    
    procesados = await generador.incrustar_chunks(chunks)
    assert len(procesados) == 2
    assert procesados[0].embedding is not None
    assert len(procesados[0].embedding) == 768
    assert procesados[1].embedding is not None
