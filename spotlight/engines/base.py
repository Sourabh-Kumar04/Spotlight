"""Base Knowledge Engine class for Spotlight."""

from abc import ABC, abstractmethod
from typing import Optional
from spotlight.models import AnswerPayload, BeatId, SceneData


class BaseKnowledgeEngine(ABC):
    """Abstract base class for beat-specific knowledge engines."""

    beat_id: BeatId

    @abstractmethod
    def can_handle_canonical(self, question: str) -> bool:
        """Returns True if the engine has a curated canonical answer for this question."""
        pass

    @abstractmethod
    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        """Returns the pre-curated, zero-latency canonical answer."""
        pass

    def normalize_question(self, question: str) -> str:
        """Helper to normalize text for flexible canonical matching."""
        import re
        q = question.lower().strip()
        q = re.sub(r"[^\w\s]", "", q)
        return " ".join(q.split())
