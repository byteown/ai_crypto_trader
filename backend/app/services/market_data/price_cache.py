from decimal import Decimal

from redis.asyncio import Redis


class PriceCache:
    def __init__(self, redis: Redis, ttl_seconds: int = 7200):
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def set_last_price(self, symbol: str, price: Decimal) -> None:
        s = str(price)
        await self.redis.set(self._key(symbol), s, ex=self.ttl_seconds)

    async def get_last_price(self, symbol: str) -> Decimal | None:
        result = await self.redis.get(self._key(symbol))
        if result is None:
            return None
        return Decimal(result)

    def _key(self, symbol) -> str:
        return f"price:{symbol}"
