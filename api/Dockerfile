FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Pillow y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear carpeta del modelo y volumen de datos
RUN mkdir -p /app/model /data

# Copiar modelo al path esperado si existe en el repo
RUN cp /app/api/model/best.pt /app/model/best.pt 2>/dev/null || true

ENV MODEL_PATH=/app/model/best.pt

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
