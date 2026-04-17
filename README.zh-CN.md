# termloop

termloop 是一个自托管的 LLM 调用中间件，帮助个人和团队在不大改现有接入方式的前提下节约 token。

它提供一个 OpenAI 兼容代理接口，并内置：

- 任务分流到不同大小模型
- 自动压缩上下文
- 请求缓存
- 把可复用的长上下文自动放入本地 RAG

## 快速开始

```bash
cp .env.example .env
pip install -e .
termloop
```

然后把客户端的 `base_url` 指向 `http://localhost:8000/v1`，并在 `.env` 中配置各家 provider 的 API key。

## 配置

termloop 使用 `TERMLOOP_PROVIDERS` 读取 JSON 格式的 provider 映射。

示例：

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

## 能力

### 1. 任务分流

分类、摘要、改写等简单任务走小模型；复杂推理和关键结果走大模型。

### 2. 自动压缩上下文

较旧的对话内容会被压缩成更短的记忆块，再送给上游模型。

### 3. Cache

相同输入的请求可以直接命中本地缓存。

### 4. 轻量 RAG

适合复用的长上下文会进入本地检索库，不再长期占用主上下文。

## 接口

- `GET /health`
- `POST /v1/chat/completions`

## 协议

MIT

