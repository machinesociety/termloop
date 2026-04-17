# termloop

**termloop** is a self-hosted OpenAI-compatible middleware focused on one mission:
make LLM products economically sustainable at scale.

We believe token efficiency is not a minor optimization. It is infrastructure.
When teams can control routing, memory, reuse, and observability, they can ship faster while keeping quality and cost predictable.

## Vision

termloop is designed as a long-term layer between applications and model providers.
It is not just a proxy. It is a policy and efficiency runtime that turns prompt traffic into measurable engineering leverage.

Core goals:

- Keep existing clients compatible through OpenAI-style APIs.
- Reduce cost with model-tier routing and deterministic cache reuse.
- Preserve output quality with controlled compression and relevance-scored RAG injection.
- Expose operational metrics so teams can reason about savings, behavior, and risk.

## Architecture

termloop request flow:

1. Receive OpenAI-compatible chat request.
2. Select provider and model tier (`small`, `medium`, `large`) using intent, length, and tool context.
3. Compress oversized history while preserving system instructions and recent critical turns.
4. Retrieve reusable long-context chunks from local RAG only if relevance passes threshold.
5. Build deterministic cache key, return cached response if valid.
6. Call upstream OpenAI-compatible provider.
7. Return response with `termloop` metadata and update metrics counters.

## DashScope (Alibaba Cloud) First

This stage defaults to DashScope OpenAI-compatible mode with Qwen tier mapping:

- `small`: `qwen-turbo`
- `medium`: `qwen-plus`
- `large`: `qwen-max`

Default base URL:

`https://dashscope.aliyuncs.com/compatible-mode/v1`

## Quick Start

```bash
cp .env.example .env
pip install -e .[dev]
termloop
```

Then point your client to:

`http://localhost:8000/v1`

## Configuration

Environment variables:

- `TERMLOOP_DASHSCOPE_API_KEY`
- `TERMLOOP_DASHSCOPE_BASE_URL`
- `TERMLOOP_PROVIDERS`
- `TERMLOOP_CACHE_ENABLED`
- `TERMLOOP_CACHE_TTL_SECONDS`
- `TERMLOOP_MAX_CONTEXT_CHARS`
- `TERMLOOP_COMPRESSION_TARGET_CHARS`
- `TERMLOOP_RAG_TRIGGER_CHARS`
- `TERMLOOP_RAG_MIN_SCORE`
- `TERMLOOP_RAG_MAX_HITS`

Provider map example:

```json
{
  "dashscope": {
    "api_key": "",
    "base_url": "",
    "small_model": "qwen-turbo",
    "medium_model": "qwen-plus",
    "large_model": "qwen-max"
  }
}
```

When fields are empty, termloop applies DashScope defaults.

## API Surface

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `GET /v1/metrics/summary`

`/v1/chat/completions` responses include `termloop` metadata:

- `provider`
- `route_tier`
- `route_reason`
- `compressed`
- `cache_hit`
- `rag_hits`

## Security and Key Handling

- Use environment variables or a secrets manager for all provider keys.
- Never commit real keys to git history, docs, screenshots, or request fixtures.
- If a key is pasted in chat or logs, rotate it immediately.
- termloop redacts detected key-like values in upstream error text.

## Quality and Testing

```bash
pytest
```

Test suite includes:

- Unit tests for routing, compression, cache TTL, RAG relevance, and config defaults.
- Integration tests for OpenAI-compatible endpoints with mocked upstream behavior.

## Roadmap

- Multi-provider adapters beyond OpenAI-compatible protocol.
- Persistent vector backends for larger retrieval corpora.
- Policy-based governance for enterprise teams (per-project budgets, model allowlists).
- Adaptive routing based on historical success and latency envelopes.
- Cost and quality dashboards built from middleware telemetry.

## License

MIT

## Chinese Guide

See [README.zh-CN.md](README.zh-CN.md).
