import os

import httpx
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

API_URL = os.getenv("API_URL", "https://api.aguacatia.warlockcode.com")

app = FastAPI(title="Aguacatia Web")
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

CLASE_INFO = {
    "unripe":      {"emoji": "🟢", "color": "green",  "label": "No apto para consumo"},
    "breaking":    {"emoji": "🟡", "color": "yellow", "label": "En transición"},
    "ripe_first":  {"emoji": "🟠", "color": "orange", "label": "Casi listo"},
    "ripe_second": {"emoji": "🟣", "color": "purple", "label": "Punto óptimo"},
    "overripe":    {"emoji": "🔴", "color": "red",    "label": "Descartar"},
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/clasificar", response_class=HTMLResponse)
async def clasificar(
    request: Request,
    file: UploadFile = File(...),
    usuario: str = Form(default="anonimo"),
):
    image_bytes = await file.read()
    error = None
    result = None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_URL}/classify",
                files={"file": (file.filename, image_bytes, file.content_type)},
                data={"usuario": usuario},
            )
        if response.status_code == 200:
            data = response.json()
            clase_info = CLASE_INFO.get(data["clase"], {})
            result = {**data, **clase_info}
        else:
            error = response.json().get("detail", "Error desconocido")
    except httpx.ConnectError:
        error = "No se pudo conectar con la API. Verifica que el servicio esté activo."
    except Exception as e:
        error = str(e)

    return templates.TemplateResponse(
        "resultado.html",
        {"request": request, "result": result, "error": error, "usuario": usuario},
    )


@app.get("/historial", response_class=HTMLResponse)
async def historial(request: Request, page: int = 1, usuario: str = ""):
    items = []
    total = 0
    error = None

    try:
        params = {"page": page, "limit": 20}
        if usuario:
            params["usuario"] = usuario

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_URL}/history", params=params)

        if response.status_code == 200:
            data = response.json()
            total = data["total"]
            items = data["items"]
            for item in items:
                item.update(CLASE_INFO.get(item["clase"], {}))
        else:
            error = "No se pudo cargar el historial"
    except Exception as e:
        error = str(e)

    return templates.TemplateResponse(
        "historial.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "page": page,
            "total_pages": max(1, (total + 19) // 20),
            "usuario": usuario,
            "error": error,
        },
    )
