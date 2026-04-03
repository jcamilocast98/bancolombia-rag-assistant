FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libxml2-dev \
        libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Crear usuario no-root
RUN useradd --create-home appuser
USER appuser

# Default: ejecutar el pipeline completo (crawl + index)
CMD ["python", "-m", "src.scraping.main"]
