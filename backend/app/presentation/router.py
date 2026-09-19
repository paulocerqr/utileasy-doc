from fastapi import APIRouter

from app.modules.documents.presentation.router import router as documents_router
from app.presentation.schemas import HealthResponse

api_router = APIRouter()
api_router.include_router(documents_router)


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
