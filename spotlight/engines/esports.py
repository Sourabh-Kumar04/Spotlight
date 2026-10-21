"""Beat 6 Knowledge Engine: Esports Team-Fight Explainer.

Canonical Question: 'Why did they lose that fight?'
Target: Coach-style breakdown of a generic team fight.
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class EsportsEngine(BaseKnowledgeEngine):
    beat_id = BeatId.ESPORTS

    CANONICAL_KEYWORDS = [
        "why did they lose that fight",
        "why did they lose the fight",
        "what went wrong",
        "why did the team lose",
        "explain the fight",
        "team fight",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="esports_coach",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Lost on Cooldowns, Not Skill",
            subtitle="COACH'S BREAKDOWN",
            verdict_badge="FIGHT ANALYSIS",
            verdict_color="purple",
            primary_explanation=(
                "Blue team lost the fight before it started: their two ultimate abilities were still "
                "on cooldown from the dragon contest 40 seconds earlier. Red team tracked that timer, "
                "forced the engage, and cleaned up 4-for-0."
            ),
            key_details=[
                "Deciding factor: ultimate cooldown tracking — red knew blue's timers.",
                "Positioning: blue's backline was split by the mid-lane wall, no peel.",
                "Lesson: never force a 5v5 within 60s of spending ultimates on an objective.",
            ],
            sources=[
                "Match VOD: Grand Finals Map 3, 28:40 (demo broadcast)",
            ],
            companion_note="Learning Companion: Fight-review concept logged. Ask about 'cooldown tracking' next.",
            latency_ms=11.0,
            is_canonical=True,
        )
