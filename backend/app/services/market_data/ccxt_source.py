from datetime import UTC, datetime
from decimal import Decimal

import ccxt.async_support as ccxt

from app.services.market_data.base import Candle


def parse_ohlcv_row(row: list) -> Candle:
    return Candle(
        datetime.fromtimestamp(row[0] / 1000, tz=UTC),
        Decimal(str(row[1])),
        Decimal(str(row[2])),
        Decimal(str(row[3])),
        Decimal(str(row[4])),
        Decimal(str(row[5])),
    )


class CcxtMarketData:
    def __init__(self, exchange_id: str):
        self.exchange_id = exchange_id

    async def fetch_candles(
        self, symbol: str, timeframe: str, limit: int
    ) -> list[Candle]:
        cls = getattr(ccxt, self.exchange_id)
        exchange = cls()
        result: list[Candle] = []
        try:
            rows = await exchange.fetch_ohlcv(
                symbol=symbol, timeframe=timeframe, limit=limit
            )
            for row in rows:
                result.append(parse_ohlcv_row(row))
        finally:
            await exchange.close()
        return result
