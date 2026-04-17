from termloop.compression import compress_messages
from termloop.models import ChatMessage


def test_compression_keeps_recent_messages() -> None:
    messages = [
        ChatMessage(role="system", content="system one"),
        ChatMessage(role="user", content="a" * 3000),
        ChatMessage(role="assistant", content="b" * 3000),
        ChatMessage(role="user", content="final question"),
    ]

    result = compress_messages(
        messages,
        target_chars=1200,
        max_context_chars=1200,
        min_preserve_turns=2,
    )

    assert result.compressed is True
    assert result.messages[-1].content == "final question"
    assert result.messages[0].role == "system"


def test_compression_skips_when_under_max_context() -> None:
    messages = [
        ChatMessage(role="system", content="policy"),
        ChatMessage(role="user", content="short request"),
    ]
    result = compress_messages(messages, target_chars=100, max_context_chars=1000, min_preserve_turns=2)
    assert result.compressed is False
