from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models.database import insert_clasificacion
from api.services import predictor, storage

router = APIRouter()

MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/classify")
async def classify(
    file: UploadFile = File(...),
    usuario: str = Form(default="anonimo"),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: {file.content_type}. Use JPG, PNG o WEBP.")

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="La imagen supera el límite de 10 MB.")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    # Subir a MinIO
    try:
        imagen_url = storage.upload_image(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al guardar la imagen: {e}")

    # Clasificar
    try:
        result = predictor.predict(image_bytes)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la clasificación: {e}")

    fecha_at = datetime.now(timezone.utc).isoformat()

    # Persistir en SQLite
    row_id = await insert_clasificacion(
        usuario=usuario,
        imagen_url=imagen_url,
        clase=result["clase"],
        confianza=result["confianza"],
        fecha_at=fecha_at,
    )

    return {
        "id": row_id,
        "clase": result["clase"],
        "clase_display": result["clase_display"],
        "confianza": result["confianza"],
        "imagen_url": imagen_url,
        "top5": result["top5"],
        "fecha_at": fecha_at,
    }
