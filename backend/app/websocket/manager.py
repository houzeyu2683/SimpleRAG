from __future__ import annotations
import asyncio
import json

import structlog
from fastapi import WebSocket

log = structlog.get_logger()


class ConnectionManager:
    def __init__(self) -> None:
        # user_id → list of active WebSocket connections
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)
        log.info("ws.connected", user_id=user_id, total=len(self._connections[user_id]))

    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        conns = self._connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(user_id, None)
        log.info("ws.disconnected", user_id=user_id)

    async def send_to_user(self, user_id: int, message: dict) -> None:
        conns = self._connections.get(user_id, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)


manager = ConnectionManager()


async def redis_subscriber(redis_url: str) -> None:
    """Background task: subscribe to Redis ingest:* channels and forward to WS."""
    import redis.asyncio as aioredis

    r = aioredis.from_url(redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.psubscribe("ingest:*")
    log.info("ws.redis_subscriber.started")

    try:
        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue
            channel: str = message["channel"]
            try:
                user_id = int(channel.split(":")[-1])
                data = json.loads(message["data"])
                await manager.send_to_user(user_id, data)
            except (ValueError, json.JSONDecodeError) as exc:
                log.warning("ws.subscriber.parse_error", error=str(exc))
    finally:
        await pubsub.unsubscribe()
        await r.aclose()
