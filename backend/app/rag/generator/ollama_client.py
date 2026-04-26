from __future__ import annotations
from collections.abc import AsyncGenerator

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()


_TIMEOUT = httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=5.0)


async def stream_chat(
    messages: list[dict],
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    import json

    model = model or settings.ollama_llm_model
    url = f"{settings.ollama_base_url}/api/chat"

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        async with client.stream(
            "POST",
            url,
            json={"model": model, "messages": messages, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
                if data.get("done"):
                    break


async def check_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False
