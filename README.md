# termloop

termloop is a self-hosted middleware for LLM calls that helps teams and individuals save tokens without rewriting their whole stack.

It acts as an OpenAI-compatible proxy and adds:

- task-aware model routing
- automatic context compression
- cache hits for repeated requests
- long-context reuse through a lightweight local RAG store

## Quick start

```bash
cp .env.example .env
pip install -e .
termloop
```

Then point your client at `http://localhost:8000/v1` and supply the provider API keys in `.env`.

## Configuration

termloop reads a JSON provider map from `TERMLOOP_PROVIDERS`.

Example:

```json
{
  "openai": {
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1",
    "small_model": "gpt-4o-mini",
    "medium_model": "gpt-4.1-mini",
    "large_model": "gpt-4.1"
  }
}
```

## Features

### 1. Task routing

Small tasks such as classification, summary, and rewrite requests are routed to smaller models. Hard reasoning and critical outputs use larger models.

### 2. Context compression

Older conversation turns can be compressed into a shorter memory block before they reach the upstream model.

### 3. Cache

Repeated requests with the same normalized inputs can be served from a local cache.

### 4. Lightweight RAG

Long reusable context can be chunked into a local retrieval store and removed from the main prompt when it is no longer needed directly.

## Endpoints

- `GET /health`
- `POST /v1/chat/completions`

## License

MIT

## Chinese guide

See [README.zh-CN.md](README.zh-CN.md).

