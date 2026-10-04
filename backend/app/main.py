from fastapi import FastAPI

from app.core.config import settings

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
