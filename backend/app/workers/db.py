from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

worker_engine = create_async_engine(settings.database_url, poolclass=NullPool)
worker_session_maker = async_sessionmaker(
    bind=worker_engine, class_=AsyncSession, expire_on_commit=False
)
