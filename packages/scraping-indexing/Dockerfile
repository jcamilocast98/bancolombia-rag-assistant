FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libxml2-dev \
        libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN opentelemetry-bootstrap -a install

# Copiar directorios completos
COPY src/ ./src/
COPY pruebas/ ./pruebas/

# Crear usuario no-root por seguridad
RUN useradd --create-home appuser
USER appuser

# Puedes sobrescribir este comando desde docker-compose
# ej. command: ["python", "-m", "src.indexacion.main"]
CMD ["opentelemetry-instrument", "python", "-m", "src.scraping.main"]

