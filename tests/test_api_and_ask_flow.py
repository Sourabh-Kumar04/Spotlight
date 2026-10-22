"""Integration tests for FastAPI endpoints, Ask flow, and WebSocket hub."""

import pytest
from fastapi.testclient import TestClient

from spotlight.main import app
from spotlight.models import BeatId, TVStatus
from spotlight.session import session_manager
from spotlight.state import state_manager

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_system_before_test():
    """Ensure clean state before each test."""
    session_manager.clear()
    state_manager.state.current_beat = BeatId.KIDS
    state_manager.state.status = TVStatus.PLAYING
    state_manager.state.is_frozen = False
    state_manager.state.current_overlay = None


def test_get_index_page():
    res = client.get("/")
    assert res.status_code == 200
    assert "SPOTLIGHT" in res.text
    assert "Fire TV App" in res.text
    assert "Phone Remote" in res.text


def test_get_tv_page():
    res = client.get("/tv")
    assert res.status_code == 200
    assert "FIRE TV 4K" in res.text
    assert "scene-canvas" in res.text

    # Demo query param
    res_demo = client.get("/tv?demo=1")
    assert res_demo.status_code == 200


def test_get_remote_page():
    res = client.get("/remote")
    assert res.status_code == 200
    assert "SPOTLIGHT" in res.text
    assert "big-ask-btn" in res.text
    assert "CURIOSITY QUESTION" in res.text


def test_get_demo_simulator_page():
    res = client.get("/demo")
    assert res.status_code == 200
    assert "SPOTLIGHT SIMULATOR" in res.text
    assert "RUN FULL 4-BEAT TOUR" in res.text


def test_api_state_and_scenes():
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.json()
    assert "state" in data
    assert "scene" in data
    assert data["state"]["current_beat"] == "kids"

    scenes_res = client.get("/api/scenes")
    assert scenes_res.status_code == 200
    scenes = scenes_res.json()
    assert "kids" in scenes
    assert "movie" in scenes
    assert "sports" in scenes
    assert "news" in scenes


def test_api_set_beat():
    res = client.post("/api/beat", json={"beat_id": "movie"})
    assert res.status_code == 200
    assert res.json()["state"]["current_beat"] == "movie"

    # Verify state endpoint reflects update
    state_res = client.get("/api/state")
    assert state_res.json()["state"]["current_beat"] == "movie"


def test_api_ask_flow_canonical_beat1_kids():
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "kids",
            "question": "Why is the sky blue?",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is True
    assert data["answer"]["title"] == "Why the Sky Is Blue"
    assert data["answer"]["verdict_badge"] == "PARENT READ-ALOUD READY"
    assert data["state"]["is_frozen"] is True
    assert data["state"]["status"] == "answered"


def test_api_ask_flow_canonical_beat2_movie():
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "movie",
            "question": "who is that man?",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is True
    assert "Cary Grant" in data["answer"]["title"]
    assert data["answer"]["verdict_badge"] == "CAST SPOTLIGHT"


def test_api_ask_flow_canonical_beat3_sports():
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "sports",
            "question": "Why was that a foul?",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is True
    assert "Reckless Challenge" in data["answer"]["title"]
    assert "DIRECT FREE KICK" in data["answer"]["verdict_badge"]


def test_api_ask_flow_canonical_beat4_news():
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "news",
            "question": "Is that claim true?",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is True
    assert data["answer"]["verdict_badge"] == "VERIFIED TRUE"
    assert len(data["answer"]["sources"]) >= 2


def test_api_ask_flow_freeform_question():
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "kids",
            "question": "What makes raindrops fall from clouds?",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is False
    assert len(data["answer"]["primary_explanation"]) > 10


def test_api_dismiss_and_reset():
    # Freeze with an ask
    client.post("/api/ask", json={"beat_id": "kids", "question": "Why is the sky blue?"})
    assert client.get("/api/state").json()["state"]["is_frozen"] is True

    # Dismiss overlay
    dismiss_res = client.post("/api/dismiss")
    assert dismiss_res.status_code == 200
    assert dismiss_res.json()["state"]["is_frozen"] is False
    assert dismiss_res.json()["state"]["status"] == "playing"

    # Reset
    reset_res = client.post("/api/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["state"]["current_beat"] == "kids"


def test_api_history_and_clear():
    client.post("/api/ask", json={"beat_id": "kids", "question": "Why is the sky blue?"})
    client.post("/api/ask", json={"beat_id": "sports", "question": "Why was that a foul?"})

    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    data = history_res.json()
    assert len(data["history"]) == 2
    assert data["stats"]["total_questions"] == 2

    # Clear history
    clear_res = client.post("/api/history/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["stats"]["total_questions"] == 0


def test_demo_script_and_execution_steps():
    script_res = client.get("/api/demo/script")
    assert script_res.status_code == 200
    script = script_res.json()["script"]
    assert len(script) == 4

    # Execute all 4 deterministic steps
    for idx in range(4):
        step_res = client.post("/api/demo/step", json={"step_index": idx})
        assert step_res.status_code == 200
        step_data = step_res.json()
        assert step_data["status"] == "demo_step_executed"
        assert step_data["answer"]["is_canonical"] is True
        assert step_data["state"]["is_frozen"] is True


def test_websocket_connection_and_actions():
    with client.websocket_connect("/ws") as ws:
        # Initial state message
        init_data = ws.receive_json()
        assert init_data["type"] == "INITIAL_STATE"

        # Send ping
        ws.send_json({"action": "ping"})
        pong_data = ws.receive_json()
        assert pong_data["type"] == "PONG"

        # Send beat change
        ws.send_json({"action": "beat", "beat_id": "sports"})
        beat_event = ws.receive_json()
        assert beat_event["type"] == "BEAT_CHANGE"
        assert beat_event["state"]["current_beat"] == "sports"


def test_api_ask_context_title_canonical_precedence():
    """Canonical engine answers must retain absolute precedence over LLM fallback."""
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "movie",
            "question": "who is that man?",
            "context_title": "Charade",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is True
    assert data["answer"]["title"] == "Cary Grant"
    assert data["answer"]["verdict_badge"] == "CAST SPOTLIGHT"
    assert "Cary Grant" in data["answer"]["primary_explanation"]
    assert data["state"]["context_title"] == "Charade"


def test_api_ask_context_title_breaking_bad():
    """Title-aware ask for Breaking Bad routes to LLM fallback and identifies Walter White / Bryan Cranston."""
    res = client.post(
        "/api/ask",
        json={
            "beat_id": "movie",
            "question": "who is the main character?",
            "context_title": "Breaking Bad",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is False
    content = (data["answer"]["title"] + " " + data["answer"]["primary_explanation"]).lower()
    assert "walter" in content or "cranston" in content or "white" in content
    assert data["session_item"]["context_title"] == "Breaking Bad"


def test_api_ask_context_title_severance_pilot():
    """Harder probe: Severance pilot director must identify Ben Stiller."""
    res = client.post(
        "/api/ask",
        json={
            "question": "who directed the pilot?",
            "context_title": "Severance",
            "source": "remote",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "answered"
    assert data["answer"]["is_canonical"] is False
    content = (data["answer"]["title"] + " " + data["answer"]["primary_explanation"]).lower()
    assert "ben stiller" in content or "stiller" in content
    assert data["state"]["context_title"] == "Severance"

