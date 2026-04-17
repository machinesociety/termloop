from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("TERMLOOP_HOST", "0.0.0.0")
    port = int(os.getenv("TERMLOOP_PORT", "8000"))
    uvicorn.run("termloop.main:app", host=host, port=port, reload=False)

