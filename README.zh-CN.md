# termloop

**termloop** 是一个自托管的 OpenAI 兼容中间件，核心目标是把 LLM 成本优化变成可持续、可度量、可工程化的基础能力。

我们把 token 节约视为基础设施，而不是“上线后再优化”的附加项。  
当团队能够统一管理路由、上下文、复用与观测，模型能力才能真正进入稳定生产。

## 愿景

termloop 不只是一个代理层，而是应用与模型供应商之间的效率运行时：

- 兼容现有 OpenAI 客户端，尽量少改接入。
- 通过模型分层与缓存复用持续降低成本。
- 通过压缩与 RAG 守卫控制质量回退风险。
- 通过聚合指标让团队能持续验证收益。

## 架构总览

请求在 termloop 内的处理流程：

1. 接收 OpenAI 兼容请求。
2. 基于任务意图、上下文长度、工具调用情况选择 `small / medium / large` 模型层。
3. 对超长历史进行压缩，保留系统消息与最近关键轮次。
4. 对可复用长上下文做本地 RAG 检索，并按相关度阈值注入。
5. 生成确定性缓存键，命中则直接返回。
6. 调用上游 OpenAI 兼容服务。
7. 回传响应，并附带 `termloop` 元数据与聚合指标。

## 阿里云 DashScope 优先

当前阶段默认面向阿里云 DashScope OpenAI 兼容模式，模型分层默认：

- `small`: `qwen-turbo`
- `medium`: `qwen-plus`
- `large`: `qwen-max`

默认地址：

`https://dashscope.aliyuncs.com/compatible-mode/v1`

## 快速开始

```bash
cp .env.example .env
pip install -e .[dev]
termloop
```

客户端 `base_url` 指向：

`http://localhost:8000/v1`

## 配置说明

主要环境变量：

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

`TERMLOOP_PROVIDERS` 示例：

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

当字段为空时，termloop 会应用 DashScope 预设。

## API 接口

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `GET /v1/metrics/summary`

`/v1/chat/completions` 会在响应中附带 `termloop` 元数据：

- `provider`
- `route_tier`
- `route_reason`
- `compressed`
- `cache_hit`
- `rag_hits`

## 安全与密钥策略

- API key 仅建议通过环境变量或密钥管理系统注入。
- 不要把真实 key 提交到仓库、文档、截图或调试样例中。
- 一旦 key 出现在聊天记录或日志中，请立即轮换。
- termloop 默认会在上游异常文本中做 key 脱敏处理。

## 测试

```bash
pytest
```

测试覆盖：

- 单元测试：路由、压缩、缓存 TTL、RAG 相关度、配置预设。
- 集成测试：OpenAI 兼容接口与端到端行为（上游 mock）。

## 路线图

- 扩展到更多 provider 适配层。
- 支持更大规模持久化向量存储。
- 增加企业级策略控制（预算、模型白名单、项目隔离）。
- 引入历史反馈驱动的自适应路由。
- 构建基于中间件遥测的成本/质量可视化面板。

## 开源协议

MIT
