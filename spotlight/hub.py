"""WebSocket hub for SPOTLIGHT multi-screen session synchronization.

Manages real-time bidirectional communication between /remote and /tv
per session (/ws/session/{session_id}). Supports voice_state events
(listening, thinking, speaking, idle) and TV control commands
(pause, play, resume, rewind, forward, volume_up, volume_down, mute, go-back).
"""

import logging
from typing import Dict, List, Optional, Set
from fastapi import WebSocket

logger = logging.getLogger("spotlight.hub")


class SessionHub:
    """Minimal WebSocket hub partitioning connections by session_id."""

    def __init__(self):
        # Maps session_id -> set of active WebSockets
        self._sessions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if session_id not in self._sessions:
            self._sessions[session_id] = set()
        self._sessions[session_id].add(websocket)
        logger.info(f"[Hub] Connected client to session '{session_id}' (total: {len(self._sessions[session_id])})")

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].discard(websocket)
            if not self._sessions[session_id]:
                del self._sessions[session_id]
            logger.info(f"[Hub] Disconnected client from session '{session_id}'")

    async def broadcast(self, session_id: str, message: dict, sender: Optional[WebSocket] = None) -> None:
        """Broadcast JSON message to all clients in session (optionally excluding sender)."""
        if session_id not in self._sessions:
            return

        dead: List[WebSocket] = []
        for ws in list(self._sessions[session_id]):
            if ws is sender:
                continue
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"[Hub] Failed to send to client in '{session_id}': {e}")
                dead.append(ws)

        for ws in dead:
            self.disconnect(session_id, ws)

    def active_sessions_count(self) -> int:
        return len(self._sessions)

    def active_connections_count(self, session_id: Optional[str] = None) -> int:
        if session_id:
            return len(self._sessions.get(session_id, set()))
        return sum(len(conns) for conns in self._sessions.values())


hub = SessionHub()
