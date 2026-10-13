import dataclasses

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candle import Candle
from app.services.market_data.base import Candle as CandleDTO


class CandleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_many(
        self, symbol: str, timeframe: str, candles: list[CandleDTO]
    ) -> None:
        if not candles:
            return

        result: list[dict] = []
        for candle in candles:
            d: dict = dataclasses.asdict(candle)
            d["symbol"] = symbol
            d["timeframe"] = timeframe
            result.append(d)
        stmt = insert(Candle).values(result)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_candles_symbol_timeframe_ts",
            set_={
                "close": stmt.excluded.close,
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "volume": stmt.excluded.volume,
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_latest(self, symbol: str, timeframe: str, limit: int) -> list[Candle]:
        stmt = (
            select(Candle)
            .where(Candle.symbol == symbol)
            .where(Candle.timeframe == timeframe)
            .order_by(Candle.ts.desc())
            .limit(limit=limit)
        )
        return list(reversed((await self.session.execute(stmt)).scalars().all()))
