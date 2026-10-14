from decimal import Decimal

from app.api.deps import get_price_cache
from app.main import app


class FakeReadCache:
    def __init__(self, prices):
        self.prices = prices

    async def get_last_price(self, symbol):
        return self.prices.get(symbol)


def test_get_price(client):
    app.dependency_overrides[get_price_cache] = lambda: FakeReadCache(
        {"BTC/USDT": Decimal("114250.12")}
    )

    response = client.get("/api/v1/prices/", params={"symbol": "BTC/USDT"})

    assert response.status_code == 200
    assert response.json() == {"symbol": "BTC/USDT", "price": "114250.12"}


def test_empty_cache(client):
    app.dependency_overrides[get_price_cache] = lambda: FakeReadCache({})

    response = client.get("/api/v1/prices/", params={"symbol": "BTC/USDT"})

    assert response.status_code == 404


def test_validation_error(client):
    app.dependency_overrides[get_price_cache] = lambda: FakeReadCache({})

    response = client.get("/api/v1/prices/", params={"symbol": "BTCUSDT"})

    assert response.status_code == 422
