from fastapi import FastAPI

from app.presentation.router import api_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="UtileasyDoc API",
        description="API for document storage and comment history.",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    application.include_router(api_router, prefix="/api")
    return application


app = create_app()
