from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_DASHSCOPE_MODELS = {
    "small_model": "qwen-turbo",
    "medium_model": "qwen-plus",
    "large_model": "qwen-max",
}


class ProviderConfig(BaseModel):
    api_key: str = ""
    base_url: str = ""
    small_model: str = DEFAULT_DASHSCOPE_MODELS["small_model"]
    medium_model: str = DEFAULT_DASHSCOPE_MODELS["medium_model"]
    large_model: str = DEFAULT_DASHSCOPE_MODELS["large_model"]

    @model_validator(mode="after")
    def validate_key_source(self) -> "ProviderConfig":
        if self.api_key.lower().startswith("file:"):
            raise ValueError("Provider api_key must come from env vars, not file paths.")
        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TERMLOOP_", extra="ignore")

    providers: str = Field(default="{}")
    dashscope_api_key: str = ""
    dashscope_base_url: str = DEFAULT_DASHSCOPE_BASE_URL
    host: str = "0.0.0.0"
    port: int = 8000
    cache_dir: str = ".termloop/cache"
    rag_dir: str = ".termloop/rag"
    max_context_chars: int = 12000
    compression_target_chars: int = 5000
    compression_min_preserve_turns: int = 4
    rag_trigger_chars: int = 6000

    def provider_map(self) -> dict[str, ProviderConfig]:
        raw: dict[str, Any] = json.loads(self.providers or "{}")
        if not raw:
            raw["dashscope"] = {}

        dashscope = raw.setdefault("dashscope", {})
        dashscope.setdefault("base_url", self.dashscope_base_url)
        dashscope.setdefault("small_model", DEFAULT_DASHSCOPE_MODELS["small_model"])
        dashscope.setdefault("medium_model", DEFAULT_DASHSCOPE_MODELS["medium_model"])
        dashscope.setdefault("large_model", DEFAULT_DASHSCOPE_MODELS["large_model"])
        if self.dashscope_api_key:
            dashscope["api_key"] = self.dashscope_api_key

        return {name: ProviderConfig(**config) for name, config in raw.items()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
