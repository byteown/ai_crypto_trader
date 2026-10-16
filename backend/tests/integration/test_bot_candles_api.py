from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

from app.api.deps import get_enqueue_fetch
from app.main import app
from app.repositories.bot import BotRepository
from app.repositories.candle import CandleRepository
from app.schemas.bot import BotCreate
from app.services.market_data.base import Candle as CandleDTO


class FakeAsyncResult:
    def __init__(self, task_id):
        self.id = task_id


class EnqueueSpy:
    def __init__(self):
        self.calls = []

    def __call__(self, symbol, timeframe):
        self.calls.append((symbol, timeframe))
        return FakeAsyncResult("fake-task-id")


def make_bot(symbol: str, timeframe: Literal[str], name: str = "John") -> BotCreate:
    return BotCreate(name=name, symbol=symbol, timeframe=timeframe)


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


async def test_bot_doesnt_exist(client):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy

    result = client.get("api/v1/bots/123/candles")

    assert result.status_code == 404


async def test_no_candles(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    repo = BotRepository(session)

    bot = await repo.create(make_bot(symbol="BTC/USDT", timeframe="1h", name="John"))

    bot_id = bot.id

    result = client.get(f"api/v1/bots/{bot_id}/candles")

    assert result.status_code == 200
    assert result.json() == []


async def test_pare_of_candles(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    bot_repo = BotRepository(session)
    candle_repo = CandleRepository(session)

    bot = await bot_repo.create(
        make_bot(symbol="BTC/USDT", timeframe="1h", name="John")
    )
    candles: list[CandleDTO] = []

    for i in range(10, 13):
        candles.append(make_candle(i))
    await candle_repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)

    candles.clear()
    for i in range(1, 3):
        candles.append(make_candle(i))
    await candle_repo.upsert_many(symbol="ETH/USDT", timeframe="1h", candles=candles)

    candles.clear()
    for i in range(1, 3):
        candles.append(make_candle(i))
    await candle_repo.upsert_many(symbol="BTC/USDT", timeframe="1d", candles=candles)

    result = client.get(f"/api/v1/bots/{bot.id}/candles")
    assert result.status_code == 200
    assert len(result.json()) == 3


async def test_candles_orders(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    bot_repo = BotRepository(session)
    candle_repo = CandleRepository(session)

    bot = await bot_repo.create(
        make_bot(symbol="BTC/USDT", timeframe="1h", name="John")
    )
    candles: list[CandleDTO] = []
    for i in range(10, 15):
        candles.append(make_candle(hour=i, close=str(100 + i)))

    await candle_repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    result = client.get(f"/api/v1/bots/{bot.id}/candles/", params={"limit": 2})

    assert result.status_code == 200
    assert len(result.json()) == 2
    assert result.json()[0]["close"] < result.json()[1]["close"]


async def test_close_accuracy(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    bot_repo = BotRepository(session)
    candle_repo = CandleRepository(session)

    bot = await bot_repo.create(
        make_bot(symbol="BTC/USDT", timeframe="1h", name="John")
    )
    candles: list[CandleDTO] = [make_candle(hour=10, close="100")]

    await candle_repo.upsert_many(symbol="BTC/USDT", timeframe="1h", candles=candles)
    result = client.get(f"/api/v1/bots/{bot.id}/candles/", params={"limit": 2})

    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0]["close"] == "100.000000000000"


async def test_limit_422(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    bot_repo = BotRepository(session)

    bot = await bot_repo.create(
        make_bot(symbol="BTC/USDT", timeframe="1h", name="John")
    )

    result = client.get(f"/api/v1/bots/{bot.id}/candles/", params={"limit": 0})
    assert result.status_code == 422

    result = client.get(f"/api/v1/bots/{bot.id}/candles/", params={"limit": 1001})
    assert result.status_code == 422


async def test_refresh_bot_exist(client, session):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy
    bot_repo = BotRepository(session)

    bot = await bot_repo.create(
        make_bot(symbol="BTC/USDT", timeframe="1h", name="John")
    )

    result = client.post(f"/api/v1/bots/{bot.id}/candles/refresh")
    assert result.json() == {"task_id": "fake-task-id"}
    assert result.status_code == 202
    assert spy.calls == [("BTC/USDT", "1h")]


async def test_refresh_bot_nonexist(client):
    spy = EnqueueSpy()
    app.dependency_overrides[get_enqueue_fetch] = lambda: spy

    result = client.post("/api/v1/bots/1337/candles/refresh")
    assert result.status_code == 404
    assert spy.calls == []
