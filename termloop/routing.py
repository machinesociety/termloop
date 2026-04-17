from __future__ import annotations

from dataclasses import dataclass

from .models import ChatCompletionRequest


SMALL_TASK_HINTS = (
    "classify",
    "classification",
    "summarize",
    "summary",
    "rewrite",
    "paraphrase",
    "translate",
    "extract",
    "tag",
    "label",
    "format",
    "grammar",
)

MEDIUM_TASK_HINTS = (
    "compare",
    "analyze",
    "explain",
    "draft",
    "review",
    "calculate",
)

HARD_TASK_HINTS = (
    "prove",
    "reason",
    "plan",
    "architecture",
    "design",
    "debug",
    "refactor",
    "safety",
    "risk",
    "root cause",
    "tradeoff",
    "threat model",
)


@dataclass(frozen=True)
class RouteDecision:
    tier: str
    model: str
    reason: str


def _text(request: ChatCompletionRequest) -> str:
    parts: list[str] = []
    for message in request.messages:
        if isinstance(message.content, str):
            parts.append(message.content)
    return "\n".join(parts).lower()


def route_request(request: ChatCompletionRequest, provider_models: dict[str, str]) -> RouteDecision:
    content = _text(request)
    length = len(content)
    requested_model = (request.model or "").strip()
    if requested_model:
        for tier, model in provider_models.items():
            if requested_model == model:
                return RouteDecision(tier, model, "explicit model request")

    small_score = sum(1 for hint in SMALL_TASK_HINTS if hint in content)
    medium_score = sum(1 for hint in MEDIUM_TASK_HINTS if hint in content)
    hard_score = sum(2 for hint in HARD_TASK_HINTS if hint in content)
    if request.tools:
        hard_score += 2
    if length > 7000:
        hard_score += 2
    elif length > 2500:
        medium_score += 1
    else:
        small_score += 1

    if hard_score >= max(3, medium_score + 1):
        return RouteDecision("large", provider_models["large"], "high complexity intent or tool context")
    if small_score >= max(2, hard_score):
        return RouteDecision("small", provider_models["small"], "lightweight task intent")
    return RouteDecision("medium", provider_models["medium"], "balanced task complexity")
