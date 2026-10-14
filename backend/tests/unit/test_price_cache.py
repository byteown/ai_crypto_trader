from decimal import Decimal

import fakeredis
import pytest

from app.services.market_data.price_cache import PriceCache


@pytest.fixture
async def cache():
    redis = fakeredis.FakeAsyncRedis(decode_responses=True)
    yield PriceCache(redis, ttl_seconds=60)
    await redis.aclose()


async def test_set_cache(cache):
    await cache.set_last_price(symbol="BTC/USDT", price=Decimal("114250.12"))
    assert await cache.get_last_price(symbol="BTC/USDT") == Decimal("114250.12")


async def test_check_accuracy(cache):
    await cache.set_last_price(symbol="BTC/USDT", price=Decimal("0.000000000123"))
    assert await cache.get_last_price(symbol="BTC/USDT") == Decimal("0.000000000123")


async def test_unknown_symbol(cache):
    assert await cache.get_last_price(symbol="UNKNOWN/UNKNOWN") is None


async def test_ttl_setting(cache):
    await cache.set_last_price(symbol="BTC/USDT", price=Decimal("0.000000000123"))
    assert await cache.redis.ttl("price:BTC/USDT") > 0


async def test_symbols_union(cache):
    await cache.set_last_price(symbol="BTC/USDT", price=Decimal(1))
    await cache.set_last_price(symbol="ETH/USDT", price=Decimal(2))
    assert await cache.get_last_price(symbol="BTC/USDT") == Decimal(1)
    assert await cache.get_last_price(symbol="ETH/USDT") == Decimal(2)
