from fastapi import APIRouter, Query

from api.models.database import get_history

router = APIRouter()


@router.get("/history")
async def history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    usuario: str | None = Query(default=None),
):
    total, items = await get_history(page=page, limit=limit, usuario=usuario)
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items,
    }
