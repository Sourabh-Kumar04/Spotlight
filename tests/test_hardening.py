"""Tests for the hardening pass: rate limits, answer cache, spoiler guard."""

from fastapi.testclient import TestClient

from spotlight.main import app

client = TestClient(app)


def test_tv_context_rate_limit():
    """Second immediate post to the same session is 429."""
    payload = {"session_id": "rl-test", "title": "T", "currentTime": "1", "paused": False}
    r1 = client.post("/api/tv/context", json=payload)
    assert r1.status_code == 200, r1.text
    r2 = client.post("/api/tv/context", json=payload)
    assert r2.status_code == 429, r2.text
    assert r2.json()["error"] == "rate_limited"


def test_tv_context_frame_size_cap():
    payload = {
        "session_id": "size-test",
        "title": "T",
        "currentTime": "1",
        "paused": False,
        "frame_b64": "A" * 2800001,
    }
    r = client.post("/api/tv/context", json=payload)
    assert r.status_code == 413, r.status_code
    assert r.json()["error"] == "frame_too_large"


def test_answer_cache_hit():
    """Same question twice: second answer served from cache (cache hit recorded)."""
    from spotlight.main import metrics

    q = {"question": "who is that man?", "context_title": "Charade", "timestamp": "42"}
    r1 = client.post("/api/ask", json=q)
    assert r1.status_code == 200, r1.text
    a1 = r1.json()["answer"]["primary_explanation"]

    hits_before = metrics.snapshot()["cache"]["hits"]
    r2 = client.post("/api/ask", json=q)
    assert r2.status_code == 200, r2.text
    a2 = r2.json()["answer"]["primary_explanation"]
    assert a1 == a2
    assert metrics.snapshot()["cache"]["hits"] > hits_before


def test_spoiler_guard_in_prompt():
    """Spoiler rule is appended when a timestamp is known, absent otherwise."""
    from spotlight.engines.llm_fallback import _spoiler_guard

    g = _spoiler_guard("00:42:15")
    assert "SPOILER RULE" in g
    assert "00:42:15" in g
    assert "Do NOT reveal" in g
    assert _spoiler_guard("") == ""
    assert _spoiler_guard(None) == ""
