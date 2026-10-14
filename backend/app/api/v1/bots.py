from typing import Annotated

from app.api.deps import BotRepoDep
from app.repositories.bot import BotNameTakenError
from app.schemas.bot import BotCreate, BotRead, BotUpdate
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1/bots", tags=["bots"])


@router.post("/", response_model=BotRead, status_code=201)
async def create_bot(data: BotCreate, repository: BotRepoDep):
    try:
        return await repository.create(data)
    except BotNameTakenError:
        raise HTTPException(status_code=409, detail="Bot name is taken") from None


@router.get("/", response_model=list[BotRead])
async def read_bots(
    repository: BotRepoDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await repository.list(limit, offset)


@router.get("/{bot_id}", response_model=BotRead)
async def read_bot(bot_id: int, repository: BotRepoDep):
    bot = await repository.get(bot_id)
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found") from None
    return bot


@router.patch("/{bot_id}", response_model=BotRead)
async def patch_bot(bot_id: int, data: BotUpdate, repository: BotRepoDep):
    bot = await repository.get(bot_id)
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found") from None

    try:
        return await repository.update(bot, data)
    except BotNameTakenError:
        raise HTTPException(status_code=409, detail="Bot name is taken") from None


@router.delete("/{bot_id}", status_code=204)
async def delete_bot(bot_id: int, repository: BotRepoDep):
    bot = await repository.get(bot_id)
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found") from None

    return await repository.delete(bot)
