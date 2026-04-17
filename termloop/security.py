from __future__ import annotations

import re


_TOKEN_PATTERN = re.compile(r"(sk-[A-Za-z0-9_-]{8})[A-Za-z0-9_-]+")


def redact_secret(value: str) -> str:
    if not value:
        return value
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}***{value[-4:]}"


def redact_text(text: str) -> str:
    if not text:
        return text
    return _TOKEN_PATTERN.sub(r"\1***", text)

