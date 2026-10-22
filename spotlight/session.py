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
            "recipes": 0,
            "esports": 0,
            "shopping": 0,
            "language": 0,
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
        if "spice" in q_lower or "recipe" in q_lower or "ingredient" in q_lower or beat_id == BeatId.COOKING:
            self.topic_counts["recipes"] += 1
        if "fight" in q_lower or "esports" in q_lower or beat_id == BeatId.ESPORTS:
            self.topic_counts["esports"] += 1
        if "wear" in q_lower or "buy" in q_lower or "shoes" in q_lower or beat_id == BeatId.SHOPPING:
            self.topic_counts["shopping"] += 1
        if "say" in q_lower or "translate" in q_lower or "mean" in q_lower or beat_id == BeatId.LANGUAGE:
            self.topic_counts["language"] += 1

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

        if beat_id == BeatId.MOVIE or "guy" in q_lower or "man" in q_lower:
            return "Learning Companion: Character saved to your Living Cast card. We'll alert you if Cary Grant's character changes identities again."

        if beat_id == BeatId.NEWS or "true" in q_lower:
            return "Learning Companion: Fact-check verified and pinned with primary citations in your Trust Feed."

        total = len(self.history) + 1
        return f"Learning Companion: Question #{total} recorded in your Fire TV Curiosity Profile."

    EXPLAINERS = {
        "fouls": {
            "title": "60-Second Explainer: Soccer Fouls",
            "body": "A foul is called when a player commits an unfair act — tripping, pushing, handling "
                    "the ball, or tackling recklessly. IFAB Law 12 sorts them into careless (no card), "
                    "reckless (yellow), and excessive force (red). The key question officials ask: did the "
                    "player endanger the opponent? If yes, the whistle blows.",
        },
        "sky": {
            "title": "60-Second Explainer: Why the Sky Is Blue",
            "body": "Sunlight holds every rainbow color. Blue light travels in short waves that bounce off "
                    "air molecules in all directions — a process called Rayleigh scattering. At sunset the light "
                    "travels farther through air, the blue scatters away, and reds and oranges remain.",
        },
        "characters": {
            "title": "60-Second Explainer: Following the Story",
            "body": "Cary Grant stars as Peter Joshua, a charming stranger aiding Audrey Hepburn's Reggie Lampert "
                    "in Paris after her husband is murdered. Throughout the film he continually changes his alias "
                    "(Alexander Dyle, Adam Canfield, Carson Dyle) before being revealed as Treasury agent Brian Cruikshank.",
        },
        "fact_checks": {
            "title": "60-Second Explainer: How Fact-Checks Work",
            "body": "A claim is checked against primary sources — mission telemetry, physical artifacts, "
                    "independent tracking. 'Verified true' means multiple independent lines of evidence agree. "
                    "One viral video is never enough; convergence of evidence is everything.",
        },
        "recipes": {
            "title": "60-Second Explainer: Blooming Spices",
            "body": "Blooming means frying ground spices in hot oil for 20-30 seconds before adding liquids. "
                    "Heat unlocks fat-soluble flavor compounds that water alone cannot extract. Never bloom on dry "
                    "heat — spices burn bitter in seconds without oil.",
        },
        "esports": {
            "title": "60-Second Explainer: Cooldown Tracking",
            "body": "Every powerful ability has a cooldown timer. Elite teams track the enemy's timers and "
                    "force fights the moment key ultimates are unavailable. Losing a fight is often decided "
                    "60 seconds earlier, at the objective that spent your cooldowns.",
        },
        "shopping": {
            "title": "60-Second Explainer: Spotted on Screen",
            "body": "Costume departments dress leads in hero pieces repeated across scenes for visual identity. "
                    "The sneakers appear in 6 scenes because they are the character's signature — spotting them "
                    "once lets you recognize the visual shorthand everywhere.",
        },
        "language": {
            "title": "60-Second Explainer: Informal vs Formal",
            "body": "'No te rindas' uses the informal 'te' — for family and friends. With strangers you would hear "
                    "'no se rinda'. Spanish encodes the relationship in the verb itself, which is why the same "
                    "phrase can sound warm or distant depending on one syllable.",
        },
    }

    def get_summary(self) -> dict:
        """Return per-topic counts plus a suggested explainer for the top topic (2+ asks)."""
        top_topic = max(self.topic_counts, key=lambda k: self.topic_counts[k])
        top_count = self.topic_counts[top_topic]
        suggestion = None
        if top_count >= 2 and top_topic in self.EXPLAINERS:
            exp = self.EXPLAINERS[top_topic]
            suggestion = {
                "topic": top_topic,
                "ask_count": top_count,
                "title": exp["title"],
                "prompt": f"You've asked about {top_topic} {top_count} times — want the 60-second explainer?",
            }
        return {
            "topic_counts": dict(self.topic_counts),
            "category_counts": dict(self.category_counts),
            "total_asks": len(self.history),
            "suggested_explainer": suggestion,
        }

    def get_explainer(self, topic: str) -> dict | None:
        exp = self.EXPLAINERS.get(topic)
        if not exp:
            return None
        return {"topic": topic, **exp}

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
