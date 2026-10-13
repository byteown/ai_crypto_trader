from datetime import UTC, datetime
from decimal import Decimal

from app.services.market_data.ccxt_source import parse_ohlcv_row


def test_market_conver():
    ROW = [1700000000000, 37000.1, 37500.0, 36900.5, 37200.25, 12.5]
    candle = parse_ohlcv_row(ROW)
    assert candle.ts == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)
    assert candle.ts.tzinfo != None
    assert candle.open == Decimal("37000.1")
    assert isinstance(candle.close, Decimal)
