from __future__ import annotations

from typing import Any

import httpx

from ..security import redact_secret, redact_text


class ProviderRequestError(RuntimeError):
    """Raised when an upstream OpenAI-compatible provider request fails."""


class OpenAICompatibleProvider:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                detail = redact_text(str(exc))
                safe_base = redact_text(self.base_url)
                safe_key = redact_secret(self.api_key)
                raise ProviderRequestError(
                    f"Upstream request failed for {safe_base} with key {safe_key}: {detail}"
                ) from exc
