from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import PriceCacheDep
from app.schemas.price import PriceRead

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


@router.get("/", response_model=PriceRead, status_code=200)
async def get_price(
    symbol: Annotated[str, Query(pattern=r"^[A-Z0-9]{2,10}/[A-Z0-9]{2,10}$")],
    cache: PriceCacheDep,
):
    result = await cache.get_last_price(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail="Price is not available") from None
    return {"symbol": symbol, "price": result}
