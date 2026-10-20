"""Session history tracking and Learning Companion layer for Spotlight."""

import uuid
from typing import Dict, List, Optional
from spotlight.models import BeatId, SessionHistoryItem


class SessionManager:
    """In-memory session history and companion insight engine."""

    def __init__(self) -> None:
        self.history: List[SessionHistoryItem] = []
        self.category_counts: Dict[str, int] = {}
        self.topic_counts: Dict[str, int] = {
            "fouls": 0,
            "sky": 0,
            "characters": 0,
            "fact_checks": 0,
        }

    def record_ask(
        self,
        beat_id: BeatId,
        category: str,
        question: str,
        answer_title: str,
        is_canonical: bool,
        latency_ms: float,
        custom_note: Optional[str] = None,
    ) -> SessionHistoryItem:
        # Detect topics
        q_lower = question.lower()
        if "foul" in q_lower or "card" in q_lower or "tackle" in q_lower or beat_id == BeatId.SPORTS:
            self.topic_counts["fouls"] += 1
        if "sky" in q_lower or "blue" in q_lower or beat_id == BeatId.KIDS:
            self.topic_counts["sky"] += 1
        if "guy" in q_lower or "who is" in q_lower or "character" in q_lower or beat_id == BeatId.MOVIE:
            self.topic_counts["characters"] += 1
        if "true" in q_lower or "claim" in q_lower or "fact" in q_lower or beat_id == BeatId.NEWS:
            self.topic_counts["fact_checks"] += 1

        self.category_counts[category] = self.category_counts.get(category, 0) + 1

        # Generate companion note if not provided
        note = custom_note or self._generate_companion_note(beat_id, question)

        item = SessionHistoryItem(
            id=str(uuid.uuid4())[:8],
            beat_id=beat_id,
            category=category,
            question=question,
            answer_title=answer_title,
            is_canonical=is_canonical,
            latency_ms=latency_ms,
            companion_note=note,
        )
        self.history.append(item)
        return item

    def _generate_companion_note(self, beat_id: BeatId, question: str) -> str:
        q_lower = question.lower()
        if beat_id == BeatId.SPORTS or "foul" in q_lower:
            count = self.topic_counts["fouls"]
            if count == 1:
                return "Learning Companion: First soccer rule logged. We will track recurring officiating calls for you."
            elif count == 2:
                return "Learning Companion: You've asked about fouls twice this week. Added Law 12 to your Sports Companion."
            else:
                return f"Learning Companion: You've asked about officiating calls {count} times. Offside & tackle breakdown saved."

        if beat_id == BeatId.KIDS or "sky" in q_lower:
            count = self.topic_counts["sky"]
            return "Learning Companion: Science question logged to Family Curiosity Journal. Great follow-up for bedtime reading."

        if beat_id == BeatId.MOVIE or "guy" in q_lower:
            return "Learning Companion: Character saved to your Living Cast card. We'll alert you if Vance appears in the climax."

        if beat_id == BeatId.NEWS or "true" in q_lower:
            return "Learning Companion: Fact-check verified and pinned with primary citations in your Trust Feed."

        total = len(self.history) + 1
        return f"Learning Companion: Question #{total} recorded in your Fire TV Curiosity Profile."

    def get_history(self) -> List[SessionHistoryItem]:
        return list(reversed(self.history))

    def get_stats(self) -> Dict[str, object]:
        return {
            "total_questions": len(self.history),
            "category_breakdown": dict(self.category_counts),
            "topic_frequencies": dict(self.topic_counts),
            "canonical_answers": sum(1 for item in self.history if item.is_canonical),
            "llm_fallbacks": sum(1 for item in self.history if not item.is_canonical),
        }

    def clear(self) -> None:
        self.history.clear()
        self.category_counts.clear()
        for k in self.topic_counts:
            self.topic_counts[k] = 0


# Global session manager instance
session_manager = SessionManager()
