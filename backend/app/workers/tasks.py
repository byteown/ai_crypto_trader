import asyncio

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.repositories.candle import CandleRepository
from app.services.market_data.ccxt_source import CcxtMarketData
from app.services.market_data.sync import sync_candles
from app.workers.celery_app import celery_app

worker_engine = create_async_engine(settings.database_url, poolclass=NullPool)
worker_session_maker = async_sessionmaker(
    bind=worker_engine, class_=AsyncSession, expire_on_commit=False
)


async def _fetch_candles(symbol: str, timeframe: str, limit: int):

    async with worker_session_maker() as session:
        data = CcxtMarketData(settings.exchange_id)
        repo = CandleRepository(session)
        return await sync_candles(
            source=data, repo=repo, symbol=symbol, timeframe=timeframe, limit=limit
        )


@celery_app.task
def fetch_candles(symbol: str, timeframe: str, limit: int = 100) -> int:
    return asyncio.run(_fetch_candles(symbol, timeframe, limit))
