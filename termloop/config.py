from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseSettings):
    api_key: str = ""
    base_url: str = ""
    small_model: str = "gpt-4o-mini"
    medium_model: str = "gpt-4.1-mini"
    large_model: str = "gpt-4.1"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TERMLOOP_", extra="ignore")

    providers: str = Field(default="{}")
    host: str = "0.0.0.0"
    port: int = 8000
    cache_dir: str = ".termloop/cache"
    rag_dir: str = ".termloop/rag"
    max_context_chars: int = 12000
    compression_target_chars: int = 5000
    rag_trigger_chars: int = 6000

    def provider_map(self) -> dict[str, ProviderConfig]:
        raw: dict[str, Any] = json.loads(self.providers or "{}")
        return {name: ProviderConfig(**config) for name, config in raw.items()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

