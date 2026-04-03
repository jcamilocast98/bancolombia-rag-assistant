# ---- Stage 1: Base ----
FROM python:3.11-slim AS base

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Development ----
FROM base AS development

COPY . .

CMD ["uvicorn", "src.interfaces.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ---- Stage 3: Production ----
FROM base AS production

COPY src/ ./src/

# Crear usuario no-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.interfaces.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
