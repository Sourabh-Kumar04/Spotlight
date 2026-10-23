"""FastAPI Main Application for Spotlight: Curiosity Remote for Fire TV."""

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from spotlight import config
from spotlight.engines.router import knowledge_router
from spotlight.hub import hub
from spotlight.intent import classify_intent
from spotlight.metrics import metrics

# --- Simple in-memory rate limiting (protects the public tunnel) ---
_rate_buckets = {}  # key -> list of hit timestamps

def _check_rate(key, max_hits, window_s):
    import time as _t
    now = _t.time()
    hits = [t for t in _rate_buckets.get(key, []) if now - t < window_s]
    if len(hits) >= max_hits:
        _rate_buckets[key] = hits
        return False
    hits.append(now)
    _rate_buckets[key] = hits
    return True
from spotlight.vision import analyze_frame
from spotlight.voice import transcribe_audio_bytes, synthesize_speech
from spotlight.models import (
    AskRequest,
    BeatId,
    TVStatus,
    VoiceTranscribeRequest,
    VoiceSpeakRequest,
    TVContextRequest,
)
from spotlight.session import session_manager
from spotlight.state import state_manager
from spotlight.tv_context import tv_context_store

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="SPOTLIGHT — Curiosity Remote for Fire TV",
    description="One tap, any screen, any question. Real-time TV pause & knowledge overlay system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and Templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- Debug Health Page (behind SPOTLIGHT_DEBUG=1) ---

@app.get("/health")
async def health():
    """Debug health page — returns runtime metrics JSON.

    Disabled unless SPOTLIGHT_DEBUG=1 env var is set.
    """
    if os.getenv("SPOTLIGHT_DEBUG", "0") != "1":
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return metrics.snapshot()


# --- Web Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Home portal with quick links to TV app, Phone Remote, and Demo split-view."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"scenes": config.SCENES, "beats": config.ORDERED_BEATS},
    )


@app.get("/tv", response_class=HTMLResponse)
@app.head("/tv", response_class=HTMLResponse)
async def get_tv_page(request: Request, demo: int = Query(0)):
    """Full-screen Fire TV app."""
    is_demo = demo == 1
    state = state_manager.get_state()
    scene = state_manager.get_scene()
    return templates.TemplateResponse(
        request=request,
        name="tv.html",
        context={
            "demo": is_demo,
            "state": state,
            "scene": scene,
            "scenes": config.SCENES,
        },
    )


@app.get("/remote", response_class=HTMLResponse)
async def get_remote_page(request: Request, demo: int = Query(0)):
    """Mobile-optimized curiosity remote with ONE big Ask button."""
    is_demo = demo == 1
    state = state_manager.get_state()
    scene = state_manager.get_scene()
    return templates.TemplateResponse(
        request=request,
        name="remote.html",
        context={
            "demo": is_demo,
            "state": state,
            "scene": scene,
            "scenes": config.SCENES,
        },
    )


@app.get("/demo", response_class=HTMLResponse)
async def get_demo_page(request: Request):
    """Side-by-side simulator view with Fire TV screen and Phone Remote."""
    return templates.TemplateResponse(
        request=request,
        name="demo.html",
        context={"scenes": config.SCENES, "beats": config.ORDERED_BEATS},
    )


# --- REST API Endpoints ---

@app.get("/api/state")
async def get_state():
    """Retrieve current TV state and scene."""
    return {
        "state": state_manager.get_state().model_dump(),
        "scene": state_manager.get_scene().model_dump(),
    }


@app.get("/api/scenes")
async def get_scenes():
    """List all 4 predefined beats and scenes."""
    return {beat.value: scene.model_dump() for beat, scene in config.SCENES.items()}


@app.post("/api/beat")
async def set_active_beat(payload: Dict[str, str]):
    """Switch active beat on the TV."""
    beat_str = payload.get("beat_id", "kids")
    try:
        beat_id = BeatId(beat_str)
    except ValueError:
        beat_id = BeatId.KIDS
    await state_manager.set_beat(beat_id)
    return {
        "status": "ok",
        "state": state_manager.get_state().model_dump(),
        "scene": state_manager.get_scene().model_dump(),
    }


@app.get("/api/companion/summary")
async def companion_summary():
    """Learning Companion: per-topic counts + suggested 60-second explainer."""
    return session_manager.get_summary()


@app.get("/api/companion/explainer/{topic}")
async def companion_explainer(topic: str):
    """Learning Companion: fetch the 60-second explainer for a topic."""
    exp = session_manager.get_explainer(topic)
    if not exp:
        return {"status": "not_found", "topic": topic}
    return {"status": "ok", **exp}


class FrameAnalysisRequest(BaseModel):
    image_b64: str  # base64-encoded JPEG/PNG, avoids multipart dependency


@app.post("/api/analyze-frame")
async def analyze_frame_endpoint(req: FrameAnalysisRequest):
    """Frame analysis: send a base64 TV frame, get scene understanding + suggested question."""
    import base64 as _b64
    try:
        data = _b64.b64decode(req.image_b64)
    except Exception:
        return {"status": "error", "detail": "invalid base64"}
    if not data or len(data) > 8 * 1024 * 1024:
        return {"status": "error", "detail": "empty file or over 8MB limit"}
    result = analyze_frame(data)
    return {"status": "ok", **result}


@app.post("/api/voice/transcribe")
async def voice_transcribe_endpoint(req: VoiceTranscribeRequest, request: Request):
    """Transcribe user audio base64 using faster-whisper with VAD & ghost-guard."""
    import base64 as _b64
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate("stt:" + client_ip, 20, 60.0):
        return JSONResponse(status_code=429, content={"error": "rate_limited", "detail": "max 20 transcriptions per minute"})
    try:
        audio_bytes = _b64.b64decode(req.audio_b64)
    if len(audio_bytes) > 10 * 1024 * 1024:
        return JSONResponse(status_code=413, content={"error": "audio_too_large", "detail": "audio over 10MB"})
    except Exception:
        return JSONResponse(status_code=400, content={"error": "invalid_base64", "text": "", "segments": []})

    _stt_start = time.perf_counter()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, transcribe_audio_bytes, audio_bytes, req.mime)
    metrics.record_stt((time.perf_counter() - _stt_start) * 1000.0)
    # Transcribed text hits the intent router first
    intent = classify_intent(result.get("text", ""))
    result["intent"] = intent
    return result


@app.post("/api/voice/speak")
async def voice_speak_endpoint(req: VoiceSpeakRequest):
    """Synthesize text to audio/wav using Piper TTS in subprocess mode."""
    wav_bytes = await synthesize_speech(req.text)
    return Response(content=wav_bytes, media_type="audio/wav")


# --- TV Self-Awareness: context capture ---

@app.post("/api/tv/context")
async def set_tv_context(req: TVContextRequest):
    """Store the latest captured TV frame + metadata per session.

    Called automatically by tv.js every 5 seconds.  The ask pipeline
    auto-attaches this context when an incoming /api/ask request has no
    explicit context_title / frame_b64.
    """
    sid = req.session_id or "default"
    if not _check_rate("tvctx:" + sid, 1, 2.0):
        return JSONResponse(status_code=429, content={"error": "rate_limited", "detail": "max 1 context post per 2s per session"})
    if req.frame_b64 and len(req.frame_b64) > 2800000:
        return JSONResponse(status_code=413, content={"error": "frame_too_large", "detail": "frame_b64 over ~2MB"})
    ctx = tv_context_store.set(
        sid,
        title=req.title,
        current_time=req.currentTime,
        paused=req.paused,
        frame_b64=req.frame_b64,
    )
    metrics.record_session_context(sid, req.title or "", bool(req.frame_b64))
    return {"status": "ok", "session_id": ctx.session_id}


@app.get("/api/tv/context/{session_id}")
async def get_tv_context(session_id: str):
    """Retrieve the latest stored TV context for a session (for debugging / probing)."""
    ctx = tv_context_store.get(session_id)
    if ctx is None:
        return {"status": "not_found", "session_id": session_id}
    return {
        "status": "ok",
        "session_id": ctx.session_id,
        "title": ctx.title,
        "currentTime": ctx.current_time,
        "paused": ctx.paused,
        "has_frame": bool(ctx.frame_b64),
    }


@app.post("/api/ask")
async def handle_ask(req: AskRequest):
    """Core Ask flow:
    1. Freeze frame & enter 'analyzing' status on TV
    2. Resolve knowledge engine (canonical instant answer or LLM fallback)
    3. Log to session history and generate learning companion note
    4. Apply answered overlay to TV state and broadcast
    """
    beat_id = req.beat_id or state_manager.get_state().current_beat
    scene = config.SCENES.get(beat_id, config.SCENES[BeatId.KIDS])
    timestamp = req.timestamp or scene.timestamp

    # --- TV self-awareness: auto-attach session context when not explicit ---
    effective_context_title = req.context_title
    effective_frame_b64 = req.frame_b64
    tv_ctx = tv_context_store.get(req.session_id)
    if tv_ctx:
        if not effective_context_title and tv_ctx.title:
            effective_context_title = tv_ctx.title
        if not effective_frame_b64 and tv_ctx.frame_b64:
            effective_frame_b64 = tv_ctx.frame_b64

    # 1. TV enters analyzing state
    await state_manager.trigger_freeze_and_analyze(
        timestamp, context_title=effective_context_title
    )

    # Small delay for realistic Fire TV analysis perception if demo mode
    # (keeps canonical feel instant yet observable)
    if req.source == "demo":
        await asyncio.sleep(0.4)

    # 2. Resolve knowledge engine
    _ask_start = time.perf_counter()
    answer = await knowledge_router.resolve_localized(
        beat_id=beat_id,
        question=req.question,
        custom_scene=scene,
        lang=getattr(req, "lang", "en") or "en",
        context_title=effective_context_title,
        frame_b64=effective_frame_b64,
    )
    metrics.record_ask((time.perf_counter() - _ask_start) * 1000.0)
    if not answer.is_canonical:
        metrics.record_llm_provider(answer.engine_id)

    # 3. Log to session history
    session_item = session_manager.record_ask(
        beat_id=beat_id,
        category=scene.category,
        question=req.question or scene.default_question,
        answer_title=answer.title,
        is_canonical=answer.is_canonical,
        latency_ms=answer.latency_ms,
        custom_note=answer.companion_note or None,
        context_title=effective_context_title,
    )
    answer.companion_note = session_item.companion_note

    # 4. Apply answer overlay & broadcast
    await state_manager.apply_answer(answer)

    return {
        "status": "answered",
        "answer": answer.model_dump(),
        "state": state_manager.get_state().model_dump(),
        "session_item": session_item.model_dump(),
    }


@app.post("/api/dismiss")
async def dismiss_overlay():
    """Dismiss the TV answer overlay and resume playback."""
    await state_manager.dismiss_overlay()
    return {"status": "ok", "state": state_manager.get_state().model_dump()}


@app.post("/api/reset")
async def reset_system():
    """Reset state machine and session history."""
    await state_manager.reset()
    session_manager.clear()
    tv_context_store.clear()
    return {"status": "reset", "state": state_manager.get_state().model_dump()}


@app.get("/api/history")
async def get_history():
    """Retrieve curiosity session history and learning companion analytics."""
    return {
        "history": [item.model_dump() for item in session_manager.get_history()],
        "stats": session_manager.get_stats(),
    }


@app.post("/api/history/clear")
async def clear_history():
    """Clear session curiosity history."""
    session_manager.clear()
    return {"status": "cleared", "stats": session_manager.get_stats()}


# --- Demo Mode API ---

DEMO_SCRIPT = [
    {
        "beat_index": 0,
        "beat_id": BeatId.KIDS.value,
        "scene_title": config.SCENES[BeatId.KIDS].title,
        "question": "Why is the sky blue?",
        "expected_verdict": "PARENT READ-ALOUD READY",
        "description": "Beat 1: Kids documentary explainer — warm, parent-friendly science.",
    },
    {
        "beat_index": 1,
        "beat_id": BeatId.MOVIE.value,
        "scene_title": config.SCENES[BeatId.MOVIE].title,
        "question": "who is that man?",
        "expected_verdict": "CAST SPOTLIGHT",
        "description": "Beat 2: Movie catch-up card — Cary Grant as Peter Joshua in Charade (1963).",
    },
    {
        "beat_index": 2,
        "beat_id": BeatId.SPORTS.value,
        "scene_title": config.SCENES[BeatId.SPORTS].title,
        "question": "Why was that a foul?",
        "expected_verdict": "DIRECT FREE KICK + YELLOW CARD",
        "description": "Beat 3: International soccer foul — replay review & IFAB Law 12 ruling.",
    },
    {
        "beat_index": 3,
        "beat_id": BeatId.NEWS.value,
        "scene_title": config.SCENES[BeatId.NEWS].title,
        "question": "Is that claim true?",
        "expected_verdict": "VERIFIED TRUE",
        "description": "Beat 4: Neutral science news fact-check — Apollo 11 moon landing + 2 sources.",
    },
]


@app.get("/api/demo/script")
async def get_demo_script():
    """Returns the deterministic 4-beat demo script."""
    return {"script": DEMO_SCRIPT}


@app.post("/api/demo/step")
async def execute_demo_step(payload: Dict[str, Any]):
    """Deterministically execute a demo step without external network dependencies."""
    beat_idx = int(payload.get("step_index", 0)) % 4
    step_data = DEMO_SCRIPT[beat_idx]
    beat_id = BeatId(step_data["beat_id"])

    # 1. Switch to the beat
    await state_manager.set_beat(beat_id)
    scene = config.SCENES[beat_id]

    # 2. Trigger freeze
    await state_manager.trigger_freeze_and_analyze(scene.timestamp)

    # 3. Resolve canonical answer directly
    answer = await knowledge_router.resolve(
        beat_id=beat_id,
        question=step_data["question"],
        custom_scene=scene,
        force_llm=False,
    )

    # 4. Record session history
    session_item = session_manager.record_ask(
        beat_id=beat_id,
        category=scene.category,
        question=step_data["question"],
        answer_title=answer.title,
        is_canonical=answer.is_canonical,
        latency_ms=answer.latency_ms,
        custom_note=answer.companion_note,
    )

    # 5. Apply answer to TV
    await state_manager.apply_answer(answer)

    return {
        "status": "demo_step_executed",
        "step_index": beat_idx,
        "step": step_data,
        "answer": answer.model_dump(),
        "state": state_manager.get_state().model_dump(),
        "session_item": session_item.model_dump(),
    }


# --- WebSocket Hub ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await state_manager.register_listener(websocket)

    # Send initial state snapshot on connect
    init_msg = {
        "type": "INITIAL_STATE",
        "state": state_manager.get_state().model_dump(),
        "scene": state_manager.get_scene().model_dump(),
        "history": [i.model_dump() for i in session_manager.get_history()],
        "stats": session_manager.get_stats(),
    }
    await websocket.send_json(init_msg)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "beat":
                beat_val = data.get("beat_id", "kids")
                try:
                    b_id = BeatId(beat_val)
                except ValueError:
                    b_id = BeatId.KIDS
                await state_manager.set_beat(b_id)

            elif action == "ask":
                beat_val = data.get("beat_id")
                b_id = BeatId(beat_val) if beat_val in BeatId._value2member_map_ else state_manager.get_state().current_beat
                q = data.get("question", "")
                ts = data.get("timestamp")
                sid = data.get("session_id", "default")
                scene = config.SCENES.get(b_id, config.SCENES[BeatId.KIDS])

                # Auto-attach TV context
                eff_title = data.get("context_title")
                eff_frame = data.get("frame_b64")
                tv_ctx = tv_context_store.get(sid)
                if tv_ctx:
                    if not eff_title and tv_ctx.title:
                        eff_title = tv_ctx.title
                    if not eff_frame and tv_ctx.frame_b64:
                        eff_frame = tv_ctx.frame_b64

                await state_manager.trigger_freeze_and_analyze(ts or scene.timestamp, context_title=eff_title)
                answer = await knowledge_router.resolve(
                    beat_id=b_id, question=q, custom_scene=scene,
                    context_title=eff_title, frame_b64=eff_frame,
                )
                session_item = session_manager.record_ask(
                    beat_id=b_id,
                    category=scene.category,
                    question=q or scene.default_question,
                    answer_title=answer.title,
                    is_canonical=answer.is_canonical,
                    latency_ms=answer.latency_ms,
                    custom_note=answer.companion_note,
                    context_title=eff_title,
                )
                answer.companion_note = session_item.companion_note
                await state_manager.apply_answer(answer)

            elif action == "dismiss":
                await state_manager.dismiss_overlay()

            elif action == "reset":
                await state_manager.reset()
                session_manager.clear()

            elif action == "ping":
                await websocket.send_json({"type": "PONG"})

    except WebSocketDisconnect:
        await state_manager.unregister_listener(websocket)
    except Exception:
        await state_manager.unregister_listener(websocket)


@app.websocket("/ws/session/{session_id}")
async def session_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Minimal WebSocket hub for /ws/session/{session_id}.
    /remote publishes {kind:"voice_state", state, transcript?} and {kind:"control", action, seconds?};
    /tv subscribes and reacts.
    """
    await hub.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await hub.broadcast(session_id, data, sender=websocket)
    except WebSocketDisconnect:
        hub.disconnect(session_id, websocket)
    except Exception:
        hub.disconnect(session_id, websocket)

