from bs4 import BeautifulSoup

class LimpiadorDatos:
    """Limpia el contenido HTML para extraer únicamente el texto principal."""

    def limpiar_html(self, contenido_html: str) -> str:
        """Remueve la navegación, pie de página, cabeceras y extrae texto útil."""
        sopa = BeautifulSoup(contenido_html, "html.parser")
        
        # Eliminar etiquetas no deseadas
        for elemento in sopa(["script", "style", "nav", "footer", "header", "aside"]):
            elemento.extract()
            
        # Obtener el texto resultante
        texto = sopa.get_text(separator="\n", strip=True)
        return texto
