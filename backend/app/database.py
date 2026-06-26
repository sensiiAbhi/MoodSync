"""
MoodSync Database Setup — Async SQLAlchemy with asyncpg
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.async_database_url,   # auto-converts postgresql:// → postgresql+asyncpg://
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """FastAPI dependency — yields async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup (dev mode — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
