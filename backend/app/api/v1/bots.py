from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import BotDep, BotRepoDep, CandleRepoDep, EnqueueFetchDep
from app.repositories.bot import BotNameTakenError
from app.schemas.bot import BotCreate, BotRead, BotUpdate
from app.schemas.candle import CandleRead, RefreshAccepted

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
async def read_bot(bot: BotDep):
    return bot


@router.patch("/{bot_id}", response_model=BotRead)
async def patch_bot(bot: BotDep, data: BotUpdate, repository: BotRepoDep):
    try:
        return await repository.update(bot, data)
    except BotNameTakenError:
        raise HTTPException(status_code=409, detail="Bot name is taken") from None


@router.delete("/{bot_id}", status_code=204)
async def delete_bot(bot: BotDep, repository: BotRepoDep):
    return await repository.delete(bot)


@router.get("/{bot_id}/candles", response_model=list[CandleRead])
async def read_bot_candles(
    bot: BotDep,
    candles: CandleRepoDep,
    limit: Annotated[int, Query(gt=0, le=1000)] = 100,
):
    return await candles.get_latest(
        symbol=bot.symbol, timeframe=bot.timeframe, limit=limit
    )


@router.post(
    "/{bot_id}/candles/refresh", response_model=RefreshAccepted, status_code=202
)
async def refresh_bot_candles(bot: BotDep, enqueue: EnqueueFetchDep):
    result = enqueue(bot.symbol, bot.timeframe)
    return RefreshAccepted(task_id=result.id)
