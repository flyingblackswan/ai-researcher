from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize global resources here (e.g., job registry, log directories)
    # TODO: wire up services once implemented
    yield
    # Cleanup resources here if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Researcher Backend API",
        version="0.1.0",
        description="Headless API for AI-Researcher workflows (research, paper generation, config, logs).",
        lifespan=lifespan,
    )

    from research_agent.config import settings
    # CORS (env-driven; "*" or empty means permissive for development)
    if settings.CORS_ORIGINS.strip() == "*" or settings.CORS_ORIGINS.strip() == "":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    from .api.v1.research import router as research_router
    from .api.v1.paper import router as paper_router
    from .api.v1.config import router as config_router
    from .api.v1.logs import router as logs_router

    app.include_router(research_router, prefix="/api/v1/research", tags=["research"])
    app.include_router(paper_router, prefix="/api/v1/paper", tags=["paper"])
    app.include_router(config_router, prefix="/api/v1/config", tags=["config"])
    app.include_router(logs_router, prefix="/api/v1/logs", tags=["logs"])

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    return app


# Uvicorn entrypoint: `uvicorn backend.app.main:app --reload --port 7039`
app = create_app()
