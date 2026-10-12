from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BotMode(Enum):
    PAPER = "paper"
    LIVE = "live"


class BotStrategy(Enum):
    RULES = "rules"
    AI = "ai"


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    symbol: Mapped[str] = mapped_column()
    timeframe: Mapped[str] = mapped_column()
    mode: Mapped[BotMode] = mapped_column(default=BotMode.PAPER)
    strategy: Mapped[BotStrategy] = mapped_column(default=BotStrategy.RULES)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
