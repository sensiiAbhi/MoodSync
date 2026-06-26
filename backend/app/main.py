"""
MoodSync FastAPI Application — Main Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup: create DB tables (graceful degradation if DB unavailable)
    try:
        await init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Database unavailable: {e}")
        print("  Server will start but DB-dependent endpoints will fail.")
        print("  Set DATABASE_URL in .env and ensure PostgreSQL is running.")
    yield
    # Shutdown



def create_app() -> FastAPI:
    app = FastAPI(
        title="MoodSync API",
        description=(
            "Context-Aware Psychological Music Recommendation Platform. "
            "Recommends music based on your emotional state, activity, and desired outcome."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Health check
    @app.get("/health", tags=["Health"])
    async def health():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.APP_ENV,
        }

    return app


app = create_app()
