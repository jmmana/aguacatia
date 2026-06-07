import os
from pathlib import Path
from typing import Any

from PIL import Image

MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/best.pt")

CLASSES = {
    0: ("unripe",      "Unripe — Verde, no apto para consumo"),
    1: ("breaking",    "Breaking — En transición"),
    2: ("ripe_first",  "Ripe First Stage — Casi listo"),
    3: ("ripe_second", "Ripe Second Stage — Punto óptimo"),
    4: ("overripe",    "Overripe — Deteriorado"),
}

_model: Any = None


def load_model():
    global _model
    if _model is None:
        from ultralytics import YOLO  # lazy import — evita crash en servers sin GPU
        model_path = Path(MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo no encontrado en {MODEL_PATH}. "
                "Entrena el modelo en Google Colab y copia best.pt a api/model/"
            )
        _model = YOLO(str(model_path))
    return _model


def is_model_loaded() -> bool:
    return _model is not None


def predict(image_bytes: bytes) -> dict:
    """
    Recibe bytes de imagen, retorna predicción con top-5.

    Returns:
        {
            "clase": "ripe_second",
            "clase_display": "Ripe Second Stage — Punto óptimo",
            "confianza": 0.91,
            "top5": [{"clase": ..., "clase_display": ..., "confianza": ...}, ...]
        }
    """
    import io
    model = load_model()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    results = model.predict(img, verbose=False)
    probs = results[0].probs

    top1_idx = int(probs.top1)
    top1_conf = float(probs.top1conf)
    top5_idxs = probs.top5
    top5_confs = probs.top5conf.tolist()

    clase_key, clase_display = CLASSES.get(top1_idx, ("unknown", "Desconocido"))

    top5 = []
    for idx, conf in zip(top5_idxs, top5_confs):
        key, display = CLASSES.get(int(idx), ("unknown", "Desconocido"))
        top5.append({"clase": key, "clase_display": display, "confianza": round(float(conf), 4)})

    return {
        "clase": clase_key,
        "clase_display": clase_display,
        "confianza": round(top1_conf, 4),
        "top5": top5,
    }
