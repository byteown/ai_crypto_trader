from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Candle:
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class MarketDataSource(Protocol):
    async def fetch_candles(
        self, symbol: str, timeframe: str, limit: int
    ) -> list[Candle]: ...
