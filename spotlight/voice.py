"""Voice subsystem for SPOTLIGHT: Curiosity Remote for Fire TV.

Provides:
1. Transcribe: faster-whisper (int8, VAD filter, word timestamps, ghost-guard)
2. Speak: Piper TTS synthesis (subprocess mode, compact English voice, audio/wav output)
"""

import asyncio
import base64
import io
import logging
import os
import shutil
import tempfile
import wave
from typing import Any, Dict, List, Optional

from spotlight import config

logger = logging.getLogger("spotlight.voice")

# Global singleton faster-whisper model
_whisper_model = None


def get_whisper_model():
    """Lazily load faster-whisper model."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info("Initializing faster-whisper model...")
            _whisper_model = WhisperModel(
                config.WHISPER_MODEL,
                device=config.WHISPER_DEVICE,
                compute_type=config.WHISPER_COMPUTE_TYPE,
            )
            logger.info("faster-whisper model initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize faster-whisper: {e}")
            raise
    return _whisper_model


def _make_silent_wav(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generate a valid silent WAV file as fallback."""
    num_samples = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)
    return buf.getvalue()


def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime: Optional[str] = None,
    no_speech_threshold: float = 0.6,
) -> Dict[str, Any]:
    """Transcribe audio bytes using faster-whisper with ghost-guard.

    Ghost-guard protection against silence hallucinations:
    - vad_filter=True, min_silence_duration_ms=500
    - condition_on_previous_text=False
    - no_speech_prob filter (> no_speech_threshold discarded)
    """
    if not audio_bytes or len(audio_bytes) < 40:
        return {"text": "", "segments": []}

    model = get_whisper_model()

    ext = ".webm"
    if mime:
        if "wav" in mime:
            ext = ".wav"
        elif "ogg" in mime:
            ext = ".ogg"
        elif "mp4" in mime:
            ext = ".mp4"
        elif "mp3" in mime or "mpeg" in mime:
            ext = ".mp3"

    segments_raw = None
    try:
        segments_iter, _ = model.transcribe(
            io.BytesIO(audio_bytes),
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            word_timestamps=True,
            condition_on_previous_text=False,
        )
        segments_raw = list(segments_iter)
    except Exception as e:
        logger.info(f"Direct stream transcription failed, retrying with tempfile: {e}")
        with tempfile.NamedTemporaryFile(suffix=ext, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            segments_iter, _ = model.transcribe(
                tmp.name,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                word_timestamps=True,
                condition_on_previous_text=False,
            )
            segments_raw = list(segments_iter)

    filtered_segments: List[Dict[str, Any]] = []
    for s in segments_raw or []:
        # Ghost-guard: drop segments with high no_speech_prob
        if s.no_speech_prob is not None and s.no_speech_prob > no_speech_threshold:
            continue

        text = (s.text or "").strip()
        if not text:
            continue

        words_data: List[Dict[str, Any]] = []
        if getattr(s, "words", None):
            for w in s.words:
                words_data.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "probability": round(w.probability, 2),
                })

        filtered_segments.append({
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": text,
            "no_speech_prob": round(s.no_speech_prob, 3) if s.no_speech_prob is not None else 0.0,
            "words": words_data,
        })

    combined_text = " ".join(seg["text"] for seg in filtered_segments).strip()
    return {
        "text": combined_text,
        "segments": filtered_segments,
    }


async def synthesize_speech(text: str) -> bytes:
    """Synthesize text to audio/wav using Piper subprocess."""
    clean_text = (text or "").strip()
    if not clean_text:
        return _make_silent_wav(0.3)

    piper_bin = config.PIPER_BINARY
    voice_model = config.PIPER_VOICE_MODEL

    if not piper_bin or not os.path.exists(piper_bin):
        candidates = [
            shutil.which("piper"),
            os.path.expanduser("~/.local/bin/piper"),
            os.path.expanduser("~/.local/share/piper/piper/piper"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "piper", "piper")),
        ]
        for c in candidates:
            if c and os.path.isfile(c) and os.access(c, os.X_OK):
                piper_bin = c
                break

    if not voice_model or not os.path.exists(voice_model):
        model_candidates = [
            os.path.expanduser("~/.local/share/piper/voices/en_US-lessac-medium.onnx"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "piper", "voices", "en_US-lessac-medium.onnx")),
        ]
        for mc in model_candidates:
            if mc and os.path.isfile(mc):
                voice_model = mc
                break

    if not piper_bin or not voice_model or not os.path.isfile(piper_bin) or not os.path.isfile(voice_model):
        logger.warning(f"Piper binary ({piper_bin}) or voice model ({voice_model}) missing; returning fallback WAV")
        return _make_silent_wav(1.0)

    try:
        proc = await asyncio.create_subprocess_exec(
            piper_bin,
            "--model",
            voice_model,
            "--output_file",
            "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(input=clean_text.encode("utf-8"))
        if proc.returncode != 0 or not stdout.startswith(b"RIFF"):
            logger.warning(f"Piper returned non-zero code {proc.returncode}: {stderr.decode('utf-8', errors='ignore')}")
            return _make_silent_wav(1.0)
        return stdout
    except Exception as e:
        logger.error(f"Piper execution exception: {e}")
        return _make_silent_wav(1.0)
