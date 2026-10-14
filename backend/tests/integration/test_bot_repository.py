from typing import Literal

from app.repositories.bot import BotRepository
from app.schemas.bot import BotCreate


def make_bot(symbol: str, timeframe: Literal[str], name: str = "John") -> BotCreate:
    return BotCreate(name=name, symbol=symbol, timeframe=timeframe)


async def test_no_bots(session):
    repo = BotRepository(session)
    assert (await repo.list_market_pairs()) == []


async def test_two_pairs(session):
    repo = BotRepository(session)
    await repo.create(make_bot(symbol="BTC/USDT", timeframe="1h", name="John1"))
    await repo.create(make_bot(symbol="BTC/USDT", timeframe="1h", name="John3"))
    await repo.create(make_bot(symbol="ETH/USDT", timeframe="4h", name="John2"))
    pairs = await repo.list_market_pairs()
    assert set(pairs) == {("BTC/USDT", "1h"), ("ETH/USDT", "4h")}


async def test_one_pair(session):
    repo = BotRepository(session)
    await repo.create(make_bot(symbol="BTC/USDT", timeframe="1h", name="John1"))
    await repo.create(make_bot(symbol="BTC/USDT", timeframe="1d", name="John3"))
    pairs = await repo.list_market_pairs()
    assert set(pairs) == {("BTC/USDT", "1h"), ("BTC/USDT", "1d")}
