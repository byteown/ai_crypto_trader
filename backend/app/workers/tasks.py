import asyncio

from app.core.config import settings
from app.repositories.bot import BotRepository
from app.repositories.candle import CandleRepository
from app.services.market_data.ccxt_source import CcxtMarketData
from app.services.market_data.sync import sync_candles
from app.workers.celery_app import celery_app
from app.workers.db import worker_session_maker


async def _fetch_candles(symbol: str, timeframe: str, limit: int) -> int:
    async with worker_session_maker() as session:
        data = CcxtMarketData(settings.exchange_id)
        repo = CandleRepository(session)
        return await sync_candles(
            source=data, repo=repo, symbol=symbol, timeframe=timeframe, limit=limit
        )


async def _sync_all_candles() -> int:
    async with worker_session_maker() as session:
        repo = BotRepository(session)
        pairs = await repo.list_market_pairs()
        for symbol, timeframe in pairs:
            fetch_candles.delay(symbol, timeframe)
        return len(pairs)


@celery_app.task
def fetch_candles(symbol: str, timeframe: str, limit: int = 100) -> int:
    return asyncio.run(_fetch_candles(symbol, timeframe, limit))


@celery_app.task
def sync_all_candles() -> int:
    return asyncio.run(_sync_all_candles())
