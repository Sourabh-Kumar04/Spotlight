"""Lightweight runtime metrics tracker for SPOTLIGHT /health debug page."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SessionInfo:
    last_context_at: float = 0.0
    title: str = ""
    has_frame: bool = False


class MetricsTracker:
    """In-memory singleton tracking runtime stats for the /health endpoint."""

    def __init__(self) -> None:
        self._start_time: float = time.time()
        self._last_stt_ms: Optional[float] = None
        self._last_llm_provider: Optional[str] = None
        self._last_ask_ms: Optional[float] = None
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._sessions: Dict[str, SessionInfo] = {}

    # --- properties ---

    @property
    def uptime_s(self) -> float:
        return round(time.time() - self._start_time, 1)

    # --- recorders ---

    def record_stt(self, ms: float) -> None:
        self._last_stt_ms = round(ms, 1)

    def record_llm_provider(self, provider: str) -> None:
        self._last_llm_provider = provider

    def record_ask(self, ms: float) -> None:
        self._last_ask_ms = round(ms, 1)

    def record_cache_hit(self) -> None:
        self._cache_hits += 1

    def record_cache_miss(self) -> None:
        self._cache_misses += 1

    def record_session_context(
        self, session_id: str, title: str, has_frame: bool
    ) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionInfo()
        s = self._sessions[session_id]
        s.last_context_at = time.time()
        s.title = title
        s.has_frame = has_frame

    # --- snapshot for /health ---

    def snapshot(self) -> dict:
        return {
            "uptime_s": self.uptime_s,
            "sessions": {
                sid: {
                    "last_context_at": s.last_context_at,
                    "title": s.title,
                    "has_frame": s.has_frame,
                }
                for sid, s in self._sessions.items()
            },
            "last_stt_ms": self._last_stt_ms,
            "last_llm_provider": self._last_llm_provider,
            "last_ask_ms": self._last_ask_ms,
            "cache": {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
            },
        }


# Global singleton — mirrors the pattern used by state_manager / session_manager
metrics = MetricsTracker()
