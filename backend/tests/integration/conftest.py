import asyncio
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_session
from app.main import app

test_engine = create_async_engine(settings.test_database_url, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_session() -> AsyncGenerator[AsyncSession]:
    async with test_async_session_maker() as session:
        yield session


async def _create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _truncate():
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE bots, candles RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    asyncio.run(_create_tables())
    yield
    asyncio.run(_drop_tables())


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    asyncio.run(_truncate())


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def session():
    async with test_async_session_maker() as s:
        yield s
