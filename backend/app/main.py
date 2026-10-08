from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/health")
async def health(session: SessionDep):
    try:
        stmt = select(1)
        await session.execute(stmt)
        return JSONResponse(content={"status": "ok", "db": "ok"}, status_code=200)
    except InterfaceError:
        return JSONResponse(
            content={"status": "error", "db": "unavailable"}, status_code=503
        )
