import boto3
import asyncio
import logging
from typing import Optional
from botocore.exceptions import ClientError
from src.dominio.entidades.pagina import Pagina
from src.dominio.puertos.puerto_almacenamiento import PuertoAlmacenamiento
from src.configuracion.ajustes import ajustes

logger = logging.getLogger(__name__)

class AdaptadorAlmacenamientoS3(PuertoAlmacenamiento):
    """Adaptador de almacenamiento real que utiliza S3 (o MinIO local)."""

    def __init__(self):
        # Configuramos el cliente de S3 para MinIO (usando endpoint_url)
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"http://{ajustes.endpoint_s3}",
            aws_access_key_id=ajustes.clave_acceso_s3,
            aws_secret_access_key=ajustes.clave_secreta_s3,
            region_name='us-east-1' # Minio suele ignorar esto pero boto3 lo pide
        )
        self.bucket = ajustes.bucket_s3
        self._asegurar_bucket()

    def _asegurar_bucket(self):
        """Verifica si el bucket existe y lo crea si no."""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creando bucket '{self.bucket}' en MinIO...")
                self.s3.create_bucket(Bucket=self.bucket)
            else:
                logger.error(f"Error verificando bucket: {e}")

    async def guardar_html_crudo(self, pagina: Pagina) -> str:
        """Guarda el objeto Pagina como un archivo JSON en S3."""
        # Usar un hash MD5 de la URL para evitar problemas de longitud o caracteres no permitidos en S3/MinIO
        import hashlib
        url_hash = hashlib.md5(str(pagina.url).encode('utf-8')).hexdigest()
        llave = f"{url_hash}.json"
        
        logger.info(f"[S3] Guardando: {pagina.url} → {llave}")
        
        # Serializar el modelo a JSON
        contenido_json = pagina.model_dump_json()

        try:
            # Boto3 es síncrono, lo ejecutamos en un hilo para no bloquear el loop
            await asyncio.to_thread(
                self.s3.put_object,
                Bucket=self.bucket,
                Key=llave,
                Body=contenido_json,
                ContentType='application/json'
            )
            logger.debug(f"Página guardada exitosamente en S3: {llave}")
            return llave
        except Exception as e:
            logger.error(f"Falla al guardar en S3 '{llave}': {e}")
            raise e

    async def obtener_html_crudo(self, ruta: str) -> Optional[str]:
        """Recupera el contenido HTML desde el JSON almacenado en S3."""
        try:
            # Obtener el objeto de S3
            response = await asyncio.to_thread(
                self.s3.get_object,
                Bucket=self.bucket,
                Key=ruta
            )
            
            # Leer el cuerpo del objeto
            contenido_json = response['Body'].read().decode('utf-8')
            
            # Descomprimir el JSON (usando la misma lógica que el simulado)
            import json
            diccionario = json.loads(contenido_json)
            return diccionario.get("contenido_html")
            
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchKey":
                logger.warning(f"No se encontró el objeto '{ruta}' en S3.")
                return None
            raise e
        except Exception as e:
            logger.error(f"Error obteniendo contenido de S3 '{ruta}': {e}")
            return None
