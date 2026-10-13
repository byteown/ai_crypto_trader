from datetime import UTC, datetime
from decimal import Decimal

from app.repositories.candle import CandleRepository
from app.services.market_data.base import Candle as CandleDTO


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


async def test_upsert(session):
    repo = CandleRepository(session)
    candles: list[CandleDTO] = []
    for i in range(10, 13):
        candles.append(make_candle(i))

    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    assert len(await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=10)) == 3


async def test_upsert_duplicates(session):
    repo = CandleRepository(session)
    candles: list[CandleDTO] = []
    for i in range(10, 13):
        candles.append(make_candle(i))

    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)

    assert len(await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=10)) == 3


async def test_insert_notclosed_candle(session):
    repo = CandleRepository(session)
    candles: list[CandleDTO] = []
    candles.append(make_candle(hour=12))

    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    candles.clear()
    candles.append(make_candle(hour=12, close="105", high="200", volume="5"))
    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    result = await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=10)

    assert len(result) == 1
    assert result[0].close == Decimal(105)
    assert result[0].high == Decimal(200)
    assert result[0].volume == Decimal(5)


async def test_multiple_timeframe(session):
    repo = CandleRepository(session)
    candles: list[CandleDTO] = []
    candles.append(make_candle(hour=1))

    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    await repo.upsert_many(symbol="BTC/USDT", timeframe="1d", candles=candles)

    result = await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=10)
    assert len(result) == 1

    result = await repo.get_latest(symbol="BTC/USDT", timeframe="1d", limit=10)
    assert len(result) == 1


async def test_right_order(session):
    repo = CandleRepository(session)
    candles: list[CandleDTO] = []
    for i in range(10, 15):
        candles.append(make_candle(hour=i))

    await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    result = await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=10)
    assert len(result) == 5

    j: int = 0
    for i in range(10, 15):
        assert result[j].ts.hour == i
        j += 1  # noqa: SIM113

    result = await repo.get_latest(symbol="BTC/USDT", timeframe="1h", limit=3)
    assert len(result) == 3

    j = 0
    for i in range(12, 15):
        assert result[j].ts.hour == i
        j += 1  # noqa: SIM113


async def test_empty_list(session):
    repo = CandleRepository(session)

    assert (
        await repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=[])
    ) is None
