"""In-memory TV context store — keeps the latest captured frame per session.

The TV client (tv.js) periodically captures a frame and POSTs it to
/api/tv/context.  The ask pipeline auto-attaches the latest context
when the incoming AskRequest has no explicit context_title / frame_b64.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TVContext:
    """Snapshot of what's on the TV screen for a given session."""

    session_id: str
    title: str = ""
    current_time: str = ""
    paused: bool = False
    frame_b64: Optional[str] = None


class TVContextStore:
    """Thread-safe-enough for FastAPI single-process; keeps latest per session."""

    def __init__(self) -> None:
        self._contexts: Dict[str, TVContext] = {}

    def set(self, session_id: str, **kwargs) -> TVContext:
        """Store / update the context for *session_id*."""
        ctx = self._contexts.get(session_id, TVContext(session_id=session_id))
        for key, value in kwargs.items():
            if hasattr(ctx, key):
                setattr(ctx, key, value)
        self._contexts[session_id] = ctx
        return ctx

    def get(self, session_id: str) -> Optional[TVContext]:
        """Return the latest context for *session_id* or ``None``."""
        return self._contexts.get(session_id)

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear one session (or all when *session_id* is ``None``)."""
        if session_id is None:
            self._contexts.clear()
        else:
            self._contexts.pop(session_id, None)


# Global singleton — mirrors the pattern used by state_manager / session_manager
tv_context_store = TVContextStore()
