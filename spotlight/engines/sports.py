"""Beat 3 Knowledge Engine: International Soccer Rules & VAR Explainer.

Canonical Question: 'Why was that a foul?'
Target: Replay description + one-line rule (reckless tackle, IFAB Law 12).
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class SportsEngine(BaseKnowledgeEngine):
    beat_id = BeatId.SPORTS

    CANONICAL_KEYWORDS = [
        "why was that a foul",
        "why foul",
        "why that foul",
        "why a foul",
        "was that a foul",
        "why whistle",
        "what was the foul",
        "why the foul",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="soccer_var_rules",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Match Official Decision: Reckless Challenge",
            subtitle="VAR & LAWS OF THE GAME REVIEW",
            verdict_badge="DIRECT FREE KICK + YELLOW CARD",
            verdict_color="rose",
            primary_explanation=(
                "At 74:12, the defending midfielder executed a late sliding tackle from behind, "
                "leading with studs off the turf and catching the attacker's trailing right ankle before any ball contact. "
                "The match referee whistled play dead immediately due to endangerment of safety."
            ),
            key_details=[
                "Official Rule: IFAB Law 12 (Fouls and Misconduct) — A direct free kick is awarded if a player commits a tackle recklessly or with excessive force.",
                "Disciplinary Sanction: Yellow Card caution confirmed for reckless lunging challenge.",
                "Replay Analysis: Zero contact on the ball; trajectory caught opponent's plant leg under momentum.",
            ],
            sources=[
                "IFAB Laws of the Game 2024/25: Law 12 (Fouls and Misconduct)",
                "Matchday Official Incident Log (74' Challenge Incident #4)",
            ],
            companion_note="Learning Companion: You've asked about fouls twice this week. Added Law 12 to your Sports Companion.",
            latency_ms=11.0,
            is_canonical=True,
        )
