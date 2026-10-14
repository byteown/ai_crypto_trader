from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.repositories.bot import BotRepository
from app.services.market_data.price_cache import PriceCache

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_repository(session: SessionDep) -> BotRepository:
    return BotRepository(session)


BotRepoDep = Annotated[BotRepository, Depends(get_repository)]

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def get_price_cache() -> PriceCache:
    return PriceCache(redis_client)


PriceCacheDep = Annotated[PriceCache, Depends(get_price_cache)]
