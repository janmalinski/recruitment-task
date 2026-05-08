from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.v1.cities_scores import router as cities_scores_router
from backend.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    app.include_router(cities_scores_router)
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse("frontend/index.html")

    return app


app = create_app()