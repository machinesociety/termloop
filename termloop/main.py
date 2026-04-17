from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import get_settings
from .models import ChatCompletionRequest
from .service import TermloopService


settings = get_settings()
service = TermloopService(settings)

app = FastAPI(title="termloop", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> dict:
    if not service.providers:
        raise HTTPException(status_code=503, detail="No providers configured")
    response = await service.chat_completions(request)
    return response.model_dump(mode="json")

