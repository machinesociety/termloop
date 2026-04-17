from __future__ import annotations

from dataclasses import dataclass

from .models import ChatMessage


@dataclass(frozen=True)
class CompressionResult:
    messages: list[ChatMessage]
    summary: str | None
    compressed: bool


def compress_messages(
    messages: list[ChatMessage],
    target_chars: int,
    max_context_chars: int,
    min_preserve_turns: int = 4,
) -> CompressionResult:
    if not messages:
        return CompressionResult(messages=messages, summary=None, compressed=False)
    if target_chars <= 0:
        return CompressionResult(messages=messages, summary=None, compressed=False)

    system_messages = [message for message in messages if message.role == "system"]
    conversation = [message for message in messages if message.role != "system"]
    sized: list[tuple[ChatMessage, int]] = [
        (message, len(message.content) if isinstance(message.content, str) else 0)
        for message in conversation
    ]
    total = sum(size for _, size in sized)
    if total <= max_context_chars:
        return CompressionResult(messages=messages, summary=None, compressed=False)

    kept: list[ChatMessage] = []
    kept_chars = 0
    for message, size in reversed(sized):
        if kept_chars + size <= target_chars:
            kept.append(message)
            kept_chars += size

    kept = list(reversed(kept))
    if len(kept) < min_preserve_turns and conversation:
        kept = conversation[-min_preserve_turns:]
    if not kept and conversation:
        kept = [conversation[-1]]

    older = conversation[: max(0, len(conversation) - len(kept))]

    if not older:
        return CompressionResult(messages=messages, summary=None, compressed=False)

    summary_bits = []
    for item in older[-8:]:
        if isinstance(item.content, str) and item.content.strip():
            summary_bits.append(f"{item.role}: {item.content.strip()[:240]}")
    summary = " | ".join(summary_bits)[:target_chars]
    if not summary.strip():
        return CompressionResult(messages=messages, summary=None, compressed=False)
    summary_message = ChatMessage(role="system", content=f"Compressed memory: {summary}")
    return CompressionResult(
        messages=[*system_messages, summary_message, *kept],
        summary=summary,
        compressed=True,
    )
