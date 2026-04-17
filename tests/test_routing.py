from termloop.models import ChatCompletionRequest, ChatMessage
from termloop.routing import route_request


def test_route_simple_task_to_small_model() -> None:
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="please summarize this report")],
    )
    route = route_request(request, {"small": "mini", "medium": "mid", "large": "big"})
    assert route.model == "mini"
    assert route.tier == "small"


def test_route_hard_task_to_large_model() -> None:
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="design a secure distributed architecture")],
    )
    route = route_request(request, {"small": "mini", "medium": "mid", "large": "big"})
    assert route.model == "big"
    assert route.tier == "large"


def test_route_explicit_model_priority() -> None:
    request = ChatCompletionRequest(
        model="mid",
        messages=[ChatMessage(role="user", content="summarize this quickly")],
    )
    route = route_request(request, {"small": "mini", "medium": "mid", "large": "big"})
    assert route.model == "mid"
    assert route.tier == "medium"


def test_route_tools_increase_complexity() -> None:
    request = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="find an implementation path")],
        tools=[{"type": "function", "function": {"name": "search_docs"}}],
    )
    route = route_request(request, {"small": "mini", "medium": "mid", "large": "big"})
    assert route.tier in {"medium", "large"}
