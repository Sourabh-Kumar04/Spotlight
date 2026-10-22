"""Pydantic data models for Spotlight: The Curiosity Remote for Fire TV."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BeatId(str, Enum):
    KIDS = "kids"
    MOVIE = "movie"
    SPORTS = "sports"
    NEWS = "news"
    COOKING = "cooking"
    ESPORTS = "esports"
    SHOPPING = "shopping"
    LANGUAGE = "language"


class TVStatus(str, Enum):
    IDLE = "idle"
    PLAYING = "playing"
    ANALYZING = "analyzing"
    ANSWERED = "answered"


class SceneData(BaseModel):
    beat_id: BeatId
    title: str
    channel: str
    category: str
    timestamp: str
    context_summary: str
    default_question: str
    visual_theme: str
    subtitle: Optional[str] = None


class AskRequest(BaseModel):
    beat_id: Optional[BeatId] = None
    scene_id: Optional[str] = None
    question: str
    timestamp: Optional[str] = None
    source: str = "remote"
    lang: str = "en"  # en | es | hi
    context_title: Optional[str] = None


class AnswerPayload(BaseModel):
    engine_id: str
    beat_id: BeatId
    question: str
    title: str
    subtitle: str
    verdict_badge: Optional[str] = None
    verdict_color: str = "sky"  # emerald, amber, rose, sky, purple
    primary_explanation: str
    key_details: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    companion_note: str = ""
    latency_ms: float = 0.0
    is_canonical: bool = True
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TVState(BaseModel):
    current_beat: BeatId = BeatId.KIDS
    status: TVStatus = TVStatus.PLAYING
    is_frozen: bool = False
    current_overlay: Optional[AnswerPayload] = None
    timestamp: str = "00:00"
    demo_mode: bool = False
    context_title: Optional[str] = None


class SessionHistoryItem(BaseModel):
    id: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    beat_id: BeatId
    category: str
    question: str
    answer_title: str
    is_canonical: bool
    latency_ms: float
    companion_note: str
    context_title: Optional[str] = None
