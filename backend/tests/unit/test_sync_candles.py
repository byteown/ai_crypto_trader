from datetime import UTC, datetime
from decimal import Decimal

from app.services.market_data.base import Candle as CandleDTO
from app.services.market_data.sync import sync_candles


def make_candle(
    hour: int, close: str = "100", high: str = "100", volume: str = "1"
) -> CandleDTO:
    return CandleDTO(
        ts=datetime(2026, 1, 1, hour, tzinfo=UTC),
        open=Decimal(100),
        high=Decimal(high),
        low=Decimal(100),
        close=Decimal(close),
        volume=Decimal(volume),
    )


class FakeMarketData:
    def __init__(self, candles):
        self.candles = candles
        self.calls = []

    async def fetch_candles(self, symbol, timeframe, limit):
        self.calls.append((symbol, timeframe, limit))
        return self.candles


class FakeCandleRepository:
    def __init__(self):
        self.saved = []

    async def upsert_many(self, symbol, timeframe, candles):
        self.saved.append((symbol, timeframe, candles))


async def test_call_once():
    candles: list[CandleDTO] = []
    for i in range(1, 6):
        candles.append(make_candle(hour=i))
    repo = FakeCandleRepository()
    data = FakeMarketData(candles)

    await sync_candles(
        source=data, repo=repo, symbol="BTC/USDT", timeframe="1h", limit=10
    )

    assert data.calls == [("BTC/USDT", "1h", 10)]


async def test_check_return():
    candles: list[CandleDTO] = []
    for i in range(1, 6):
        candles.append(make_candle(hour=i))
    repo = FakeCandleRepository()
    data = FakeMarketData(candles)

    await sync_candles(
        source=data, repo=repo, symbol="BTC/USDT", timeframe="1h", limit=10
    )

    assert repo.saved == [("BTC/USDT", "1h", candles)]


async def test_how_many_returns():
    candles: list[CandleDTO] = []
    for i in range(1, 6):
        candles.append(make_candle(hour=i))
    repo = FakeCandleRepository()
    data = FakeMarketData(candles)

    assert (
        await sync_candles(
            source=data, repo=repo, symbol="BTC/USDT", timeframe="1h", limit=10
        )
    ) == 5


async def test_empty_list():
    candles: list[CandleDTO] = []
    repo = FakeCandleRepository()
    data = FakeMarketData(candles)

    assert (
        await sync_candles(
            source=data, repo=repo, symbol="BTC/USDT", timeframe="1h", limit=10
        )
    ) == 0
