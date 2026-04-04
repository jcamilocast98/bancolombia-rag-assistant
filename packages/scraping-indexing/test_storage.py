import asyncio
import sys
import os

# Asegurar que el directorio src sea importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.dominio.entidades.pagina import Pagina
from src.infraestructura.adaptador_almacenamiento_s3 import AdaptadorAlmacenamientoS3

async def test_minio_integration():
    print("--- Iniciando prueba de Integración con MinIO ---")
    
    # 1. Instanciar el adaptador
    try:
        adaptador = AdaptadorAlmacenamientoS3()
        print(" [OK] Adaptador instanciado correctamente.")
    except Exception as e:
        print(f" [ERROR] No se pudo instanciar el adaptador. ¿Está MinIO corriendo? Error: {e}")
        return

    # 2. Crear una página de prueba
    pagina_test = Pagina(
        url="https://www.bancolombia.com/prueba-minio",
        titulo="Página de Prueba MinIO",
        contenido_html="<html><body><h1>Hola MinIO</h1></body></html>",
        codigo_estado=200
    )

    # 3. Guardar en MinIO
    print(" Intentando guardar HTML en MinIO...")
    try:
        llave = await adaptador.guardar_html_crudo(pagina_test)
        print(f" [OK] Página guardada con llave: {llave}")
    except Exception as e:
        print(f" [ERROR] Error al guardar: {e}")
        return

    # 4. Recuperar desde MinIO
    print(" Intentando recuperar HTML desde MinIO...")
    try:
        html_recuperado = await adaptador.obtener_html_crudo(llave)
        if html_recuperado == pagina_test.contenido_html:
            print(" [OK] El contenido recuperado coincide con el original.")
        else:
            print(f" [FALTA] El contenido NO coincide. Recuperado: {html_recuperado}")
    except Exception as e:
        print(f" [ERROR] Error al recuperar: {e}")

    print("--- Prueba finalizada ---")

if __name__ == "__main__":
    asyncio.run(test_minio_integration())
