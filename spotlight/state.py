"""State machine and WebSocket event hub for Spotlight."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket

from spotlight import config
from spotlight.models import AnswerPayload, BeatId, SceneData, TVState, TVStatus

logger = logging.getLogger("spotlight.state")


class StateManager:
    """Central state machine managing playback, freeze, and overlay display."""

    def __init__(self) -> None:
        self.state = TVState(
            current_beat=BeatId.KIDS,
            status=TVStatus.PLAYING,
            is_frozen=False,
            current_overlay=None,
            timestamp=config.SCENES[BeatId.KIDS].timestamp,
            demo_mode=False,
        )
        self._listeners: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    def get_state(self) -> TVState:
        return self.state

    def get_scene(self) -> SceneData:
        return config.SCENES.get(self.state.current_beat, config.SCENES[BeatId.KIDS])

    async def register_listener(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._listeners.add(websocket)

    async def unregister_listener(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._listeners.discard(websocket)

    async def broadcast_state(self, event_type: str = "STATE_UPDATE", extra: Optional[Dict[str, Any]] = None) -> None:
        payload = {
            "type": event_type,
            "state": self.state.model_dump(),
            "scene": self.get_scene().model_dump(),
            **(extra or {}),
        }
        msg = json.dumps(payload)

        # Broadcast to all connected WebSockets
        dead_sockets: List[WebSocket] = []
        async with self._lock:
            listeners = list(self._listeners)

        for ws in listeners:
            try:
                await ws.send_text(msg)
            except Exception:
                dead_sockets.append(ws)

        if dead_sockets:
            async with self._lock:
                for ws in dead_sockets:
                    self._listeners.discard(ws)

    async def set_beat(self, beat_id: BeatId) -> None:
        if beat_id not in config.SCENES:
            beat_id = BeatId.KIDS
        self.state.current_beat = beat_id
        self.state.timestamp = config.SCENES[beat_id].timestamp
        self.state.status = TVStatus.PLAYING
        self.state.is_frozen = False
        self.state.current_overlay = None
        self.state.context_title = None
        await self.broadcast_state("BEAT_CHANGE")

    async def trigger_freeze_and_analyze(
        self, timestamp: Optional[str] = None, context_title: Optional[str] = None
    ) -> None:
        self.state.is_frozen = True
        self.state.status = TVStatus.ANALYZING
        if timestamp:
            self.state.timestamp = timestamp
        if context_title is not None:
            self.state.context_title = context_title
        await self.broadcast_state("FREEZE")

    async def apply_answer(self, answer: AnswerPayload) -> None:
        self.state.is_frozen = True
        self.state.status = TVStatus.ANSWERED
        self.state.current_overlay = answer
        await self.broadcast_state("ANSWER", {"answer": answer.model_dump()})

    async def dismiss_overlay(self) -> None:
        self.state.is_frozen = False
        self.state.status = TVStatus.PLAYING
        self.state.current_overlay = None
        await self.broadcast_state("UNFREEZE")

    async def reset(self) -> None:
        self.state.current_beat = BeatId.KIDS
        self.state.status = TVStatus.PLAYING
        self.state.is_frozen = False
        self.state.current_overlay = None
        self.state.timestamp = config.SCENES[BeatId.KIDS].timestamp
        self.state.demo_mode = False
        self.state.context_title = None
        await self.broadcast_state("RESET")


# Global state manager instance
state_manager = StateManager()
