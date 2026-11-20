# syntax=docker/dockerfile:1

# ---- 1. Compilar el frontend (Vite) ----
FROM node:22-slim AS frontend
WORKDIR /app
COPY agrocontrol-frontend/package.json agrocontrol-frontend/package-lock.json ./
RUN npm ci
COPY agrocontrol-frontend/ ./
RUN npm run build

# ---- 2. Backend Flask + SWI-Prolog + build del frontend ----
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AGROCONTROL_DB_PATH=/data/agrocontrol.db \
    PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends swi-prolog-nox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /app/dist ./agrocontrol-frontend/dist

RUN mkdir -p /data
EXPOSE 8080
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 60 app:app"]
