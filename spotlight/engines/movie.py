"""Beat 2 Knowledge Engine: Movie Context & Catch-Up Card.

Canonical Question: 'Who is that man?' (or 'Who is that guy and why is everyone mad at him?')
Target: Catch-up card (character, context, what's happening) for Charade (1963).
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class MovieEngine(BaseKnowledgeEngine):
    beat_id = BeatId.MOVIE

    CANONICAL_KEYWORDS = [
        "who is that guy",
        "why is everyone mad",
        "who is that",
        "who is that man",
        "why are they mad",
        "who is vance",
        "why is everyone angry",
        "catch up",
        "what is happening",
        "whats happening",
        "cary grant",
        "peter joshua",
        "charade",
        "alexander dyle",
        "adam canfield",
        "carson dyle",
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
            title="Cary Grant",
            subtitle="CHARADE (1963) — PETER JOSHUA",
            verdict_badge="CAST SPOTLIGHT",
            verdict_color="sky",
            primary_explanation=(
                "That is Hollywood leading man Cary Grant starring as Peter Joshua in Stanley Donen's 1963 romantic mystery thriller 'Charade'. "
                "In the film, he portrays a charming stranger who assists Reggie Lampert (Audrey Hepburn) in Paris after her husband is murdered, "
                "continually shifting through multiple aliases — Peter Joshua, Alexander Dyle, Adam Canfield, and Carson Dyle — "
                "before ultimately revealing his true identity as U.S. Treasury agent Brian Cruikshank."
            ),
            key_details=[
                "Film & Director: Charade, directed by Stanley Donen, released in 1963 by Universal Pictures.",
                "Actor & Character: Cary Grant as Peter Joshua, the charming mystery man assisting Audrey Hepburn's Reggie Lampert.",
                "The Alias Twist: Switches identities from Peter Joshua to Alexander Dyle, Adam Canfield, and Carson Dyle; secretly Treasury agent Brian Cruikshank.",
                "Public Domain Note: Entered the public domain immediately upon release in 1963 because Universal omitted the required copyright notice.",
            ],
            sources=[
                "Film Registry: Charade (Universal Pictures, 1963) — Directed by Stanley Donen",
                "Living Cast Dossier: Cary Grant (as Peter Joshua / Alexander Dyle / Brian Cruikshank)",
            ],
            companion_note="Learning Companion: Character saved to your Living Cast card. We'll alert you whenever Cary Grant's character changes identities.",
            latency_ms=14.0,
            is_canonical=True,
        )
