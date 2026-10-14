from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate


class BotNameTakenError(Exception):
    pass


class BotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, bot_id: int) -> Bot | None:
        return await self.session.get(Bot, bot_id)

    async def list(self, limit: int, offset: int) -> list[Bot]:
        stmt = select(Bot).limit(limit).offset(offset).order_by(Bot.id)
        return (await self.session.execute(stmt)).scalars().all()

    async def create(self, data: BotCreate) -> Bot:
        bot = Bot(**data.model_dump())
        self.session.add(bot)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise BotNameTakenError from e
        await self.session.refresh(bot)
        return bot

    async def update(self, bot: Bot, data: BotUpdate) -> Bot:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(bot, key, value)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise BotNameTakenError from e
        await self.session.refresh(bot)
        return bot

    async def delete(self, bot: Bot) -> None:
        await self.session.delete(bot)
        await self.session.commit()

    async def list_market_pairs(self) -> list[tuple[str, str]]:
        stmt = select(Bot.symbol, Bot.timeframe).distinct()
        result = await self.session.execute(stmt)
        return [tuple(row) for row in result.all()]
