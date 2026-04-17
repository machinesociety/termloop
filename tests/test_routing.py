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

