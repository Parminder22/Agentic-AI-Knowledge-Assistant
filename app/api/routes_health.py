from fastapi import APIRouter
from app.schemas.response_models import HealthResponse
from app.services.faiss_index import index_stats
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    faiss = index_stats()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        services={
            "api": "ok",
            "faiss": f"ok ({faiss['total_vectors']} vectors)",
            "database": "ok",
        },
    )
