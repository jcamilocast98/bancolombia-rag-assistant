import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from src.dominio.entidades.pagina import Pagina
from src.dominio.excepciones import ErrorProcesamientoHTML, ErrorExtraccionContenido
from src.configuracion.ajustes import ajustes


class ExtractorContenido:
    """Extrae el contenido crudo (HTML) de una página web."""
    
    def __init__(self, agente_usuario: str = ajustes.agente_usuario):
        self.agente_usuario = agente_usuario

    async def descargar_pagina(self, url: str) -> Pagina:
        """Descarga la URL y devuelve la entidad Pagina."""
        try:
            async with httpx.AsyncClient(headers={"User-Agent": self.agente_usuario}) as cliente:
                respuesta = await cliente.get(url, timeout=15.0, follow_redirects=True)
                
                titulo = ""
                if respuesta.status_code == 200:
                    try:
                        sopa = BeautifulSoup(respuesta.text, "html.parser")
                        if sopa.title:
                            titulo = sopa.title.string.strip() if sopa.title.string else ""
                    except Exception as e:
                        raise ErrorProcesamientoHTML(f"Fallo al procesar el título de {url}: {e}")
                
                return Pagina(
                    url=str(respuesta.url),
                    titulo=titulo,
                    contenido_html=respuesta.text,
                    codigo_estado=respuesta.status_code
                )
        except httpx.RequestError as e:
            raise ErrorExtraccionContenido(f"Petición HTTP fallida para {url}: {e}")
