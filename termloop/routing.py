from __future__ import annotations

from dataclasses import dataclass

from .models import ChatCompletionRequest


SMALL_TASK_HINTS = {
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
}

HARD_TASK_HINTS = {
    "prove",
    "reason",
    "plan",
    "architecture",
    "design",
    "debug",
    "refactor",
    "safety",
    "risk",
}


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
    hints_small = sum(1 for hint in SMALL_TASK_HINTS if hint in content)
    hints_hard = sum(1 for hint in HARD_TASK_HINTS if hint in content)

    if hints_hard > 0 or length > 8000:
        return RouteDecision("large", provider_models["large"], "hard reasoning or long prompt")
    if hints_small > 0 or length < 1200:
        return RouteDecision("small", provider_models["small"], "simple task or short prompt")
    return RouteDecision("medium", provider_models["medium"], "default balanced routing")

