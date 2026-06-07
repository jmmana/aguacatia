FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Pillow y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear carpeta de datos (modelo queda en /app/api/model/best.pt)
RUN mkdir -p /data

# MODEL_PATH apunta al modelo tal como queda en la imagen tras COPY . .
ENV MODEL_PATH=/app/api/model/best.pt

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
