from decimal import Decimal

from pydantic import BaseModel


class PriceRead(BaseModel):
    symbol: str
    price: Decimal
