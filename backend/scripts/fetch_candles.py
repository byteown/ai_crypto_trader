import asyncio

from app.core.config import settings
from app.services.market_data.ccxt_source import CcxtMarketData


async def main():
    data = CcxtMarketData(settings.exchange_id)
    candles = await data.fetch_candles(symbol="BTC/USDT", timeframe="1h", limit=10)
    for candle in candles:
        print(candle)


asyncio.run(main())
