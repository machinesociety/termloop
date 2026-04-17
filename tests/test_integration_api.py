from __future__ import annotations

from fastapi.testclient import TestClient

import termloop.main as main_module
from termloop.config import Settings
from termloop.service import TermloopService


def _build_service(tmp_path) -> TermloopService:
    settings = Settings(
        providers='{"dashscope":{"api_key":"sk-test-token","base_url":"https://dashscope.aliyuncs.com/compatible-mode/v1","small_model":"qwen-turbo","medium_model":"qwen-plus","large_model":"qwen-max"}}',
        cache_dir=str(tmp_path / "cache"),
        rag_dir=str(tmp_path / "rag"),
        cache_enabled=True,
        cache_ttl_seconds=600,
        max_context_chars=1200,
        compression_target_chars=500,
        rag_trigger_chars=300,
        rag_min_score=0.1,
    )
    return TermloopService(settings)


def test_health_and_models_endpoint(tmp_path) -> None:
    original_service = main_module.service
    main_module.service = _build_service(tmp_path)
    try:
        client = TestClient(main_module.app)
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        models = client.get("/v1/models")
        assert models.status_code == 200
        data = models.json()["data"]
        assert any(item["id"] == "qwen-turbo" for item in data)
    finally:
        main_module.service = original_service


def test_chat_completion_openai_compatible_flow(monkeypatch, tmp_path) -> None:
    async def fake_chat(self, payload):  # noqa: ANN001
        return {
            "id": "chatcmpl-integration",
            "object": "chat.completion",
            "created": 1700000000,
            "model": payload["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

    monkeypatch.setattr(
        "termloop.providers.openai_compatible.OpenAICompatibleProvider.chat_completions",
        fake_chat,
    )

    original_service = main_module.service
    main_module.service = _build_service(tmp_path)
    try:
        client = TestClient(main_module.app)
        payload = {
            "messages": [{"role": "user", "content": "summarize this quickly"}],
            "stream": False,
        }
        first = client.post("/v1/chat/completions", json=payload)
        assert first.status_code == 200
        assert first.json()["termloop"]["cache_hit"] is False

        second = client.post("/v1/chat/completions", json=payload)
        assert second.status_code == 200
        assert second.json()["termloop"]["cache_hit"] is True

        metrics = client.get("/v1/metrics/summary")
        assert metrics.status_code == 200
        assert metrics.json()["data"]["total_requests"] >= 2
    finally:
        main_module.service = original_service

