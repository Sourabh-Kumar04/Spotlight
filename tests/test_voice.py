"""Tests for /api/voice/transcribe and /api/voice/speak endpoints."""

import base64
import io
import wave
import pytest
from fastapi.testclient import TestClient

from spotlight.main import app
from spotlight.voice import _make_silent_wav, synthesize_speech

client = TestClient(app)


def _generate_silent_wav_b64(duration_s: float = 2.0, sample_rate: int = 16000) -> str:
    """Generate base64 encoded silent WAV."""
    num_samples = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)
    return base64.b64encode(buf.getvalue()).decode()


def test_voice_speak_endpoint_returns_wav():
    """POST /api/voice/speak converts text to audio/wav with RIFF header."""
    res = client.post("/api/voice/speak", json={"text": "Why is the sky blue?"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert res.content.startswith(b"RIFF")
    assert b"WAVE" in res.content[:16]
    assert len(res.content) > 5000


def test_voice_speak_empty_text_returns_valid_wav():
    """POST /api/voice/speak handles empty text gracefully with a silent WAV."""
    res = client.post("/api/voice/speak", json={"text": "   "})
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert res.content.startswith(b"RIFF")
    assert b"WAVE" in res.content[:16]


@pytest.mark.asyncio
async def test_voice_transcribe_real_audio():
    """POST /api/voice/transcribe transcribes spoken audio into text and segments."""
    # Synthesize audio to transcribe using Piper
    wav_bytes = await synthesize_speech("Spotlight Curiosity Remote")
    b64_audio = base64.b64encode(wav_bytes).decode()

    res = client.post(
        "/api/voice/transcribe",
        json={"audio_b64": b64_audio, "mime": "audio/wav"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "text" in data
    assert "segments" in data
    assert len(data["text"]) > 0
    # Must capture at least one key word from the phrase
    lower_text = data["text"].lower()
    assert "spotlight" in lower_text or "curiosity" in lower_text or "remote" in lower_text
    assert len(data["segments"]) > 0
    first_seg = data["segments"][0]
    assert "start" in first_seg
    assert "end" in first_seg
    assert "text" in first_seg
    assert "no_speech_prob" in first_seg


def test_voice_transcribe_silence_ghost_guard():
    """Ghost-guard ensures pure silence produces empty text instead of hallucinations."""
    silence_b64 = _generate_silent_wav_b64(duration_s=2.0)
    res = client.post(
        "/api/voice/transcribe",
        json={"audio_b64": silence_b64, "mime": "audio/wav"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["text"] == ""
    assert data["segments"] == []


def test_voice_transcribe_invalid_base64():
    """Invalid base64 payload returns 400 error."""
    res = client.post(
        "/api/voice/transcribe",
        json={"audio_b64": "@@@invalid_base64$$$", "mime": "audio/webm"},
    )
    assert res.status_code == 400
    data = res.json()
    assert "error" in data


def test_remote_page_has_push_to_talk_button():
    """Verify /remote contains the push-to-talk voice button."""
    res = client.get("/remote")
    assert res.status_code == 200
    assert "micBtn" in res.text
    assert "PUSH TO TALK" in res.text

