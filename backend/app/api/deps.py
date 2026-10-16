from collections.abc import Callable
from typing import Annotated

from celery.result import AsyncResult
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models import Bot
from app.repositories.bot import BotRepository
from app.repositories.candle import CandleRepository
from app.services.market_data.price_cache import PriceCache
from app.workers.tasks import fetch_candles

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_bot_repository(session: SessionDep) -> BotRepository:
    return BotRepository(session)


BotRepoDep = Annotated[BotRepository, Depends(get_bot_repository)]

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def get_price_cache() -> PriceCache:
    return PriceCache(redis_client)


PriceCacheDep = Annotated[PriceCache, Depends(get_price_cache)]


async def get_bot_or_404(bot_id: int, repository: BotRepoDep) -> Bot:
    bot = await repository.get(bot_id)

    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found") from None

    return bot


BotDep = Annotated[Bot, Depends(get_bot_or_404)]


def get_candle_repository(session: SessionDep) -> CandleRepository:
    return CandleRepository(session)


CandleRepoDep = Annotated[CandleRepository, Depends(get_candle_repository)]


def get_enqueue_fetch():
    return fetch_candles.delay


EnqueueFetchDep = Annotated[Callable[..., AsyncResult], Depends(get_enqueue_fetch)]
