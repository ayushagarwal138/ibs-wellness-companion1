"""
Database configuration and connection management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from typing import AsyncGenerator
import logging
import ssl

from app.core.config import settings

logger = logging.getLogger(__name__)

# Strip any query params from the URL (e.g. ?sslmode=require from Neon)
# since asyncpg handles SSL via connect_args, not URL params
_db_url = settings.DATABASE_URL.split("?")[0]

# Enable SSL for non-localhost connections (required for Neon, Render, Supabase, etc.)
_is_local = any(h in _db_url for h in ["localhost", "127.0.0.1"])
_connect_args = {}
if not _is_local:
    _ssl_ctx = ssl.create_default_context()
    _connect_args = {"ssl": _ssl_ctx}

# Create async engine
engine = create_async_engine(
    _db_url,
    echo=settings.DATABASE_ECHO,
    future=True,
    connect_args=_connect_args,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Base class for all models
class Base(DeclarativeBase):
    """Base class for all database models."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": ("fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"),
            "pk": "pk_%(table_name)s",
        }
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import user, symptom, medication, diet  # noqa

        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def drop_tables():
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
