from decimal import Decimal

from app.repositories.candle import CandleRepository
from app.services.market_data.base import Candle, MarketDataSource
from app.services.market_data.price_cache import PriceCache


async def sync_candles(
    source: MarketDataSource,
    repo: CandleRepository,
    symbol: str,
    timeframe: str,
    limit: int,
    price_cache: PriceCache | None = None,
) -> int:
    candles: list[Candle] = await source.fetch_candles(
        symbol=symbol, timeframe=timeframe, limit=limit
    )
    await repo.upsert_many(symbol=symbol, timeframe=timeframe, candles=candles)
    length = len(candles)

    if price_cache is not None and length > 0:
        await price_cache.set_last_price(
            symbol=symbol, price=Decimal(candles[-1].close)
        )

    return length
