from app.repositories.candle import CandleRepository
from app.services.market_data.base import Candle, MarketDataSource


async def sync_candles(
    source: MarketDataSource,
    repo: CandleRepository,
    symbol: str,
    timeframe: str,
    limit: int,
) -> int:
    candles: list[Candle] = await source.fetch_candles(
        symbol=symbol, timeframe=timeframe, limit=limit
    )
    await repo.upsert_many(symbol=symbol, timeframe=timeframe, candles=candles)
    return len(candles)
