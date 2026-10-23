"""Tests for TV self-awareness: context store and auto-attach in ask pipeline."""

import pytest
from fastapi.testclient import TestClient

from spotlight.main import app
from spotlight.models import BeatId, TVStatus
from spotlight.session import session_manager
from spotlight.state import state_manager
from spotlight.tv_context import tv_context_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_system_before_test():
    """Ensure clean state before each test."""
    session_manager.clear()
    tv_context_store.clear()
    state_manager.state.current_beat = BeatId.KIDS
    state_manager.state.status = TVStatus.PLAYING
    state_manager.state.is_frozen = False
    state_manager.state.current_overlay = None


# ── 1. Context store set/get ──────────────────────────────────────────────

def test_tv_context_store_set_and_get():
    """TVContextStore.set stores context and .get retrieves it."""
    ctx = tv_context_store.set("s1", title="Madrid vs Milan", current_time="74:12", paused=False, frame_b64="abc")
    assert ctx.session_id == "s1"
    assert ctx.title == "Madrid vs Milan"
    assert ctx.current_time == "74:12"
    assert ctx.frame_b64 == "abc"

    retrieved = tv_context_store.get("s1")
    assert retrieved is not None
    assert retrieved.title == "Madrid vs Milan"

    # Unknown session returns None
    assert tv_context_store.get("nonexistent") is None


# ── 2. Auto-attach fills missing context ──────────────────────────────────

def test_auto_attach_fills_missing_context():
    """When /api/ask has no explicit context_title, auto-attach fills it from the session's latest tv_context."""
    # Simulate TV client posting context
    client.post("/api/tv/context", json={
        "session_id": "default",
        "title": "The Syndicate Protocol",
        "currentTime": "00:15:30",
        "paused": False,
        "frame_b64": None,
    })

    # Ask without explicit context_title — should auto-attach
    res = client.post("/api/ask", json={
        "beat_id": "movie",
        "question": "who is the main character?",
        "source": "remote",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    # The auto-attached title must show in the state and session item
    assert data["state"]["context_title"] == "The Syndicate Protocol"
    assert data["session_item"]["context_title"] == "The Syndicate Protocol"


# ── 3. Explicit context wins over auto-attach ─────────────────────────────

def test_explicit_context_wins_over_auto_attach():
    """When /api/ask provides an explicit context_title, it overrides the session's tv_context."""
    # Session has TV context
    client.post("/api/tv/context", json={
        "session_id": "default",
        "title": "Some Other Show",
        "currentTime": "00:05:00",
        "paused": False,
        "frame_b64": None,
    })

    # Ask with explicit context_title — must win
    res = client.post("/api/ask", json={
        "beat_id": "movie",
        "question": "who is that man?",
        "context_title": "Charade",
        "source": "remote",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["state"]["context_title"] == "Charade"
    assert data["session_item"]["context_title"] == "Charade"
