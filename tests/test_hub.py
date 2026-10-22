"""Tests for /ws/session/{session_id} WebSocket hub."""

import pytest
from fastapi.testclient import TestClient
from spotlight.main import app
from spotlight.hub import hub


def test_session_hub_broadcast():
    client = TestClient(app)
    session_id = "test-session-123"

    with client.websocket_connect(f"/ws/session/{session_id}") as ws_remote:
        with client.websocket_connect(f"/ws/session/{session_id}") as ws_tv:
            # Remote publishes voice_state
            voice_msg = {
                "kind": "voice_state",
                "state": "listening",
                "transcript": "who is that",
            }
            ws_remote.send_json(voice_msg)

            # TV receives the broadcast
            received = ws_tv.receive_json()
            assert received == voice_msg

            # Remote publishes control command
            control_msg = {
                "kind": "control",
                "action": "rewind",
                "seconds": 30,
            }
            ws_remote.send_json(control_msg)

            # TV receives control command
            received_ctrl = ws_tv.receive_json()
            assert received_ctrl == control_msg


def test_session_isolation():
    client = TestClient(app)

    with client.websocket_connect("/ws/session/roomA") as ws_a:
        with client.websocket_connect("/ws/session/roomB") as ws_b:
            # Message sent to roomA should NOT be received by roomB
            ws_a.send_json({"kind": "control", "action": "pause"})
            # To verify roomB is isolated, we send a message in roomB and check it gets its own
            with client.websocket_connect("/ws/session/roomB") as ws_b2:
                ws_b2.send_json({"kind": "control", "action": "play"})
                received = ws_b.receive_json()
                assert received["action"] == "play"
