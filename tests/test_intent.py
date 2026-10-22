"""Tests for intent router and duration parsing."""

import pytest
from spotlight.intent import classify_intent, parse_duration, route_intent


def test_classify_commands_pause():
    res = classify_intent("pause")
    assert res["type"] == "command"
    assert res["action"] == "pause"

    res = classify_intent("Pause the video")
    assert res["type"] == "command"
    assert res["action"] == "pause"

    res = classify_intent("freeze")
    assert res["type"] == "command"
    assert res["action"] == "pause"


def test_classify_commands_play_resume():
    res = classify_intent("play")
    assert res["type"] == "command"
    assert res["action"] == "play"

    res = classify_intent("resume")
    assert res["type"] == "command"
    assert res["action"] == "resume"

    res = classify_intent("resume playback")
    assert res["type"] == "command"
    assert res["action"] == "resume"

    res = classify_intent("unpause")
    assert res["type"] == "command"
    assert res["action"] == "play"


def test_classify_commands_rewind_with_durations():
    res = classify_intent("rewind 30 seconds")
    assert res["type"] == "command"
    assert res["action"] == "rewind"
    assert res["seconds"] == 30

    res = classify_intent("back 10 seconds")
    assert res["type"] == "command"
    assert res["action"] == "rewind"
    assert res["seconds"] == 10

    res = classify_intent("go back 15 seconds")
    assert res["type"] == "command"
    assert res["action"] == "rewind"
    assert res["seconds"] == 15

    res = classify_intent("rewind 1 minute")
    assert res["type"] == "command"
    assert res["action"] == "rewind"
    assert res["seconds"] == 60

    res = classify_intent("skip back 20s")
    assert res["type"] == "command"
    assert res["action"] == "rewind"
    assert res["seconds"] == 20


def test_classify_commands_forward_with_durations():
    res = classify_intent("forward 1 minute")
    assert res["type"] == "command"
    assert res["action"] == "forward"
    assert res["seconds"] == 60

    res = classify_intent("fast forward 30 seconds")
    assert res["type"] == "command"
    assert res["action"] == "forward"
    assert res["seconds"] == 30

    res = classify_intent("skip ahead 45 seconds")
    assert res["type"] == "command"
    assert res["action"] == "forward"
    assert res["seconds"] == 45

    res = classify_intent("jump forward 2 minutes")
    assert res["type"] == "command"
    assert res["action"] == "forward"
    assert res["seconds"] == 120


def test_classify_commands_volume():
    res = classify_intent("volume up")
    assert res["type"] == "command"
    assert res["action"] == "volume_up"

    res = classify_intent("louder")
    assert res["type"] == "command"
    assert res["action"] == "volume_up"

    res = classify_intent("turn it up")
    assert res["type"] == "command"
    assert res["action"] == "volume_up"

    res = classify_intent("volume down")
    assert res["type"] == "command"
    assert res["action"] == "volume_down"

    res = classify_intent("quieter")
    assert res["type"] == "command"
    assert res["action"] == "volume_down"

    res = classify_intent("turn it down")
    assert res["type"] == "command"
    assert res["action"] == "volume_down"

    res = classify_intent("mute")
    assert res["type"] == "command"
    assert res["action"] == "mute"

    res = classify_intent("unmute")
    assert res["type"] == "command"
    assert res["action"] == "mute"


def test_classify_commands_go_back():
    res = classify_intent("go-back")
    assert res["type"] == "command"
    assert res["action"] == "go-back"

    res = classify_intent("go back")
    assert res["type"] == "command"
    assert res["action"] == "go-back"

    res = classify_intent("dismiss")
    assert res["type"] == "command"
    assert res["action"] == "go-back"


def test_classify_questions():
    res = classify_intent("who is that man")
    assert res["type"] == "question"
    assert "who is that man" in res["question"]

    res = classify_intent("Why is the sky blue?")
    assert res["type"] == "question"

    res = classify_intent("Why was that a foul?")
    assert res["type"] == "question"

    res = classify_intent("Is that claim true?")
    assert res["type"] == "question"

    res = classify_intent("What spice did they just add?")
    assert res["type"] == "question"

    res = classify_intent("Who plays Peter Joshua?")
    assert res["type"] == "question"


def test_duration_parsing_units():
    assert parse_duration("30 seconds") == 30
    assert parse_duration("10s") == 10
    assert parse_duration("15 secs") == 15
    assert parse_duration("1 minute") == 60
    assert parse_duration("2 minutes") == 120
    assert parse_duration("half a minute") == 30
    assert parse_duration("a minute") == 60
    assert parse_duration("thirty seconds") == 30
    assert parse_duration("ten seconds") == 10
    assert parse_duration("two minutes") == 120
    assert parse_duration("no numbers here", default=10) == 10


def test_transcribe_endpoint_includes_intent(monkeypatch):
    from fastapi.testclient import TestClient
    from spotlight.main import app

    # Mock transcribe_audio_bytes to avoid needing model load for unit test
    def mock_transcribe(audio_bytes, mime=None):
        return {"text": "pause", "segments": []}

    monkeypatch.setattr("spotlight.main.transcribe_audio_bytes", mock_transcribe)

    client = TestClient(app)
    import base64
    b64 = base64.b64encode(b"dummywavbytes12345678901234567890123456789012").decode()
    res = client.post("/api/voice/transcribe", json={"audio_b64": b64, "mime": "audio/wav"})
    assert res.status_code == 200
    data = res.json()
    assert "intent" in data
    assert data["intent"]["type"] == "command"
    assert data["intent"]["action"] == "pause"

