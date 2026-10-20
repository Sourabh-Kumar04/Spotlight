"""Beat 2 Knowledge Engine: Movie Context & Catch-Up Card.

Canonical Question: 'Who is that guy and why is everyone mad at him?'
Target: Catch-up card (character, context, what's happening) for a generic fictional scene.
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class MovieEngine(BaseKnowledgeEngine):
    beat_id = BeatId.MOVIE

    CANONICAL_KEYWORDS = [
        "who is that guy",
        "why is everyone mad",
        "who is that",
        "why are they mad",
        "who is vance",
        "why is everyone angry",
        "catch up",
        "what is happening",
        "whats happening",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="movie_catchup",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Catch-Up Card: Director Vance",
            subtitle="CHARACTER INTEL & TIMELINE CONTEXT",
            verdict_badge="ROGUE ASSET ALERT",
            verdict_color="amber",
            primary_explanation=(
                "That is Director Vance, former head of the covert Cyber Operations unit. "
                "Ten minutes ago at the docks, he double-crossed his own strike team and stole the biometric master cipher key. "
                "The room is furious because the facility doors just initiated a hard lockout — without Vance's cipher, everyone inside is trapped in under 15 minutes."
            ),
            key_details=[
                "Character: Director Vance (former Division Chief turned black-market broker).",
                "Context: Handed false tracking coordinates to Agent Rossi at timestamp 01:02:18.",
                "Immediate Stake: If the team cannot recover the physical key, the base mainframe self-purges at 01:30:00.",
            ],
            sources=[
                "Scene Intelligence: The Syndicate Protocol (Act II Scene 4)",
                "Living Cast Metadata: Biometric Registry Dossier #882",
            ],
            companion_note="Learning Companion: Character saved to your Living Cast card. We'll alert you if Vance appears in the climax.",
            latency_ms=14.0,
            is_canonical=True,
        )
