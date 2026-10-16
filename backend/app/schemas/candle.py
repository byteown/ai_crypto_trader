from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CandleRead(BaseModel):
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    model_config = ConfigDict(from_attributes=True)


class RefreshAccepted(BaseModel):
    task_id: str
