from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.bot import BotRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_repository(session: SessionDep) -> BotRepository:
    return BotRepository(session)


BotRepoDep = Annotated[BotRepository, Depends(get_repository)]
