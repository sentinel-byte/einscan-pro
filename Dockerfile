# --- ETAPA 1: Construir el Frontend ---
FROM node:18-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- ETAPA 2: Configurar el Backend y Runtime ---
FROM python:3.11-slim
WORKDIR /app

# Instalar dependencias del sistema (OpenCV, Tesseract, Poppler)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*


# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el backend
COPY backend/ ./backend/

# CREAR CARPETAS DE DATOS (Solución al error de Render)
RUN mkdir -p data/sheets data/scans data/exports

# Copiar el frontend compilado desde la ETAPA 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
