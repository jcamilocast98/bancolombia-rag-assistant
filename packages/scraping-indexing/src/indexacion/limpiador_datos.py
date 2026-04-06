from bs4 import BeautifulSoup
import re

class LimpiadorDatos:
    """Limpia el contenido HTML para extraer únicamente el texto principal."""

    def limpiar_html(self, contenido_html: str) -> str:
        """Remueve la navegación, pie de página, cabeceras y extrae texto útil."""
        sopa = BeautifulSoup(contenido_html, "html.parser")
        
        # Eliminar etiquetas no deseadas semánticas
        for elemento in sopa(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "svg"]):
            elemento.extract()
            
        # Eliminar contenedores por clase o ID sospechosos de ser menús o ruido
        ruido_css = ["menu", "nav", "footer", "header", "sidebar", "cookie", "modal", "popup", "banner", "breadcrumb", "cabecera", "pie-pagina", "skip-link", "sr-only", "login"]
        for elemento in sopa.find_all(attrs={"class": lambda c: c and any(r in c.lower() for r in ruido_css)}):
            elemento.extract()
            
        for elemento in sopa.find_all(attrs={"id": lambda i: i and any(r in i.lower() for r in ruido_css)}):
            elemento.extract()
            
        # Obtener el texto resultante
        texto = sopa.get_text(separator="\n", strip=True)
        # Limpiar múltiples saltos de línea consecutivos
        texto = re.sub(r'\n+', '\n', texto)
        return texto
