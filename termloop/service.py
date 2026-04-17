from __future__ import annotations

from time import time
from typing import Any
from uuid import uuid4

from .cache import CacheStore
from .compression import compress_messages
from .config import ProviderConfig, Settings
from .models import ChatCompletionChoice, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from .rag import RagStore
from .routing import route_request
from .providers.openai_compatible import OpenAICompatibleProvider


def _usage(prompt_text: str, completion_text: str) -> dict[str, int]:
    prompt_tokens = max(1, len(prompt_text) // 4)
    completion_tokens = max(1, len(completion_text) // 4)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


class TermloopService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.cache = CacheStore(settings.cache_dir)
        self.rag = RagStore(settings.rag_dir)
        self.providers = self._build_providers(settings)

    def _build_providers(self, settings: Settings) -> dict[str, dict[str, Any]]:
        providers: dict[str, dict[str, Any]] = {}
        for name, provider in settings.provider_map().items():
            providers[name] = {
                "config": provider,
                "client": OpenAICompatibleProvider(provider.api_key, provider.base_url),
            }
        return providers

    def _default_provider(self) -> tuple[str, dict[str, Any]]:
        if not self.providers:
            raise RuntimeError("No providers configured")
        return next(iter(self.providers.items()))

    def _selected_provider(self, request: ChatCompletionRequest) -> tuple[str, dict[str, Any]]:
        requested_model = (request.model or "").strip()
        if requested_model:
            for name, entry in self.providers.items():
                provider: ProviderConfig = entry["config"]
                if requested_model in {
                    provider.small_model,
                    provider.medium_model,
                    provider.large_model,
                }:
                    return name, entry
        return self._default_provider()

    def _provider_models(self, provider: ProviderConfig) -> dict[str, str]:
        return {
            "small": provider.small_model,
            "medium": provider.medium_model,
            "large": provider.large_model,
        }

    def _cache_payload(
        self,
        request: ChatCompletionRequest,
        provider_name: str,
        model: str,
        compressed: bool,
        rag_hits: list[str],
    ) -> dict[str, Any]:
        return {
            "provider": provider_name,
            "model": model,
            "messages": [message.model_dump(mode="json") for message in request.messages],
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
            "tools": request.tools,
            "tool_choice": request.tool_choice,
            "response_format": request.response_format,
            "compressed": compressed,
            "rag_hits": rag_hits,
        }

    def _chat_summary(self, request: ChatCompletionRequest, route_model: str, rag_hits: list[str], compressed: bool) -> ChatCompletionResponse:
        prompt = "\n".join(
            message.content if isinstance(message.content, str) else "" for message in request.messages
        )
        relevant = " ".join(rag_hits).strip()
        completion = (
            f"termloop routed this request to {route_model}. "
            f"Compressed={compressed}. "
            f"RAG={'enabled' if rag_hits else 'empty'}. "
            f"{relevant[:500]}"
        ).strip()
        choice = ChatCompletionChoice(index=0, message=ChatMessage(role="assistant", content=completion))
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4().hex}",
            created=int(time()),
            model=route_model,
            choices=[choice],
            usage=_usage(prompt, completion),
            termloop={
                "compressed": compressed,
                "rag_hits": rag_hits,
                "provider_model": route_model,
            },
        )

    async def chat_completions(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        provider_name, entry = self._selected_provider(request)
        provider: ProviderConfig = entry["config"]
        client: OpenAICompatibleProvider = entry["client"]
        models = self._provider_models(provider)
        route = route_request(request, models)
        compressed_request = compress_messages(request.messages, self.settings.compression_target_chars)
        prompt_text = "\n".join(
            message.content if isinstance(message.content, str) else "" for message in compressed_request.messages
        )

        rag_hits: list[str] = []
        if len(prompt_text) > self.settings.rag_trigger_chars:
            for chunk in self.rag.search(prompt_text):
                rag_hits.append(chunk.text)
            if not rag_hits:
                stored = self.rag.add_text(f"{provider_name}:{route.model}", prompt_text)
                rag_hits = [chunk.text for chunk in stored[:2]]

        cache_payload = self._cache_payload(
            request,
            provider_name,
            route.model,
            compressed_request.compressed,
            rag_hits,
        )
        cached = self.cache.get(cache_payload)
        if cached:
            return ChatCompletionResponse(**cached)

        if not provider.api_key or not provider.base_url:
            response = self._chat_summary(request, route.model, rag_hits, compressed_request.compressed)
            payload = response.model_dump(mode="json")
            payload["termloop"] = {
                "provider": provider_name,
                "route_tier": route.tier,
                "route_reason": route.reason,
                "compressed": compressed_request.compressed,
                "rag_hits": rag_hits,
                "demo_mode": True,
            }
            self.cache.set(cache_payload, payload)
            return ChatCompletionResponse(**payload)

        upstream_payload = {
            **request.model_dump(exclude_none=True),
            "model": route.model,
            "stream": False,
            "messages": [message.model_dump(exclude_none=True) for message in compressed_request.messages],
        }
        response = await client.chat_completions(upstream_payload)
        response["termloop"] = {
            "provider": provider_name,
            "route_tier": route.tier,
            "route_reason": route.reason,
            "compressed": compressed_request.compressed,
            "rag_hits": rag_hits,
        }
        self.cache.set(cache_payload, response)
        return ChatCompletionResponse(**response)
