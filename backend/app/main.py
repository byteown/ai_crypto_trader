from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import InterfaceError

from app.api.deps import SessionDep
from app.api.v1 import bots, prices

app = FastAPI()


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


app.include_router(bots.router)
app.include_router(prices.router)
