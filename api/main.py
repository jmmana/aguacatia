from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models.database import init_db
from api.routes import classify, history
from api.services.predictor import is_model_loaded, load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        load_model()
    except FileNotFoundError:
        pass  # API arranca sin modelo — /health lo reporta
    yield


app = FastAPI(
    title="Aguacatia API",
    description="Clasificación visual de aguacates Hass mediante YOLOv8",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aguacatia.warlockcode.com", "http://localhost:5000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(classify.router)
app.include_router(history.router)


@app.get("/health")
async def health():
    return {"status": "ok", "model": "loaded" if is_model_loaded() else "not_loaded"}
