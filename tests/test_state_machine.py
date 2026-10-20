"""Unit tests for the TV State Machine and event hub."""

from unittest.mock import AsyncMock
import pytest

from spotlight.models import AnswerPayload, BeatId, TVStatus
from spotlight.state import StateManager


@pytest.mark.asyncio
async def test_state_machine_initial_state():
    mgr = StateManager()
    state = mgr.get_state()
    assert state.current_beat == BeatId.KIDS
    assert state.status == TVStatus.PLAYING
    assert state.is_frozen is False
    assert state.current_overlay is None


@pytest.mark.asyncio
async def test_state_machine_freeze_and_analyze():
    mgr = StateManager()
    await mgr.trigger_freeze_and_analyze(timestamp="14:28")
    state = mgr.get_state()
    assert state.is_frozen is True
    assert state.status == TVStatus.ANALYZING
    assert state.timestamp == "14:28"


@pytest.mark.asyncio
async def test_state_machine_apply_answer():
    mgr = StateManager()
    ans = AnswerPayload(
        engine_id="test_engine",
        beat_id=BeatId.KIDS,
        question="Why is the sky blue?",
        title="Test Answer",
        subtitle="TEST SUBTITLE",
        primary_explanation="This is a test explanation.",
    )
    await mgr.apply_answer(ans)
    state = mgr.get_state()
    assert state.is_frozen is True
    assert state.status == TVStatus.ANSWERED
    assert state.current_overlay is not None
    assert state.current_overlay.title == "Test Answer"


@pytest.mark.asyncio
async def test_state_machine_dismiss_overlay():
    mgr = StateManager()
    await mgr.trigger_freeze_and_analyze("10:00")
    await mgr.dismiss_overlay()
    state = mgr.get_state()
    assert state.is_frozen is False
    assert state.status == TVStatus.PLAYING
    assert state.current_overlay is None


@pytest.mark.asyncio
async def test_state_machine_set_beat():
    mgr = StateManager()
    await mgr.set_beat(BeatId.MOVIE)
    state = mgr.get_state()
    assert state.current_beat == BeatId.MOVIE
    assert state.status == TVStatus.PLAYING
    assert state.is_frozen is False

    # Invalid beat falls back to KIDS
    await mgr.set_beat("invalid_beat")  # type: ignore
    state = mgr.get_state()
    assert state.current_beat == BeatId.KIDS


@pytest.mark.asyncio
async def test_state_machine_reset():
    mgr = StateManager()
    await mgr.set_beat(BeatId.SPORTS)
    await mgr.trigger_freeze_and_analyze("74:12")
    await mgr.reset()
    state = mgr.get_state()
    assert state.current_beat == BeatId.KIDS
    assert state.status == TVStatus.PLAYING
    assert state.is_frozen is False
    assert state.current_overlay is None


@pytest.mark.asyncio
async def test_state_machine_websocket_broadcast():
    mgr = StateManager()
    mock_ws = AsyncMock()
    await mgr.register_listener(mock_ws)
    assert mock_ws in mgr._listeners

    await mgr.broadcast_state("TEST_EVENT", {"foo": "bar"})
    mock_ws.send_text.assert_awaited_once()

    await mgr.unregister_listener(mock_ws)
    assert mock_ws not in mgr._listeners
