from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router as api_router
from .deps.container import init_container
from .middleware.logging import RequestLoggingMiddleware
from .middleware.metrics import MetricsMiddleware
from .middleware.request_context import RequestContextMiddleware
from .settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    init_container(settings)

    app = FastAPI(
        title="AI FinTech Risk Intelligence Platform - Risk API",
        version="1.0.0",
    )

    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestContextMiddleware)

    app.include_router(api_router)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(str(static_dir / "index.html"))
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse(static_dir / "favicon.ico")

    @app.get("/apple-touch-icon.png", include_in_schema=False)
    def apple_icon():
        return FileResponse(static_dir / "apple-touch-icon.png")

    @app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
    def apple_icon_pre():
        return FileResponse(static_dir / "apple-touch-icon.png")

    return app


app = create_app()