from __future__ import annotations

from dataclasses import dataclass

from .models import ChatMessage


@dataclass(frozen=True)
class CompressionResult:
    messages: list[ChatMessage]
    summary: str | None
    compressed: bool


def compress_messages(messages: list[ChatMessage], target_chars: int) -> CompressionResult:
    total = 0
    kept: list[ChatMessage] = []
    older: list[ChatMessage] = []

    for message in messages:
        content = message.content if isinstance(message.content, str) else ""
        total += len(content)
        if total > target_chars:
            older.append(message)
        else:
            kept.append(message)

    if not older:
        return CompressionResult(messages=messages, summary=None, compressed=False)

    summary_bits = []
    for item in older[-8:]:
        if isinstance(item.content, str) and item.content.strip():
            summary_bits.append(f"{item.role}: {item.content.strip()[:240]}")
    summary = " | ".join(summary_bits)[:target_chars]
    summary_message = ChatMessage(role="system", content=f"Compressed memory: {summary}")
    return CompressionResult(messages=[summary_message, *kept], summary=summary, compressed=True)

