from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.bot import BotMode, BotStrategy

BotName = Annotated[str, Field(min_length=3, max_length=30)]
Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d", "1w"]


class BotCreate(BaseModel):
    name: BotName
    symbol: str = Field(pattern=r"^[A-Z0-9]{2,10}/[A-Z0-9]{2,10}$")
    timeframe: Timeframe
    mode: BotMode = Field(default=BotMode.PAPER)
    strategy: BotStrategy = Field(default=BotStrategy.RULES)


class BotUpdate(BaseModel):
    name: BotName | None = Field(default=None)
    symbol: str | None = Field(pattern=r"^[A-Z0-9]{2,10}/[A-Z0-9]{2,10}$", default=None)
    timeframe: Timeframe | None = Field(default=None)
    mode: BotMode | None = Field(default=None)
    strategy: BotStrategy | None = Field(default=None)


class BotRead(BaseModel):
    id: int
    name: str
    symbol: str
    timeframe: str
    mode: BotMode
    strategy: BotStrategy
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
