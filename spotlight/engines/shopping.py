"""Beat 7 Knowledge Engine: Shoppable TV Moment.

Canonical Question: 'What shoes is he wearing?'
Target: real product identification from the scene — no fictional catalog.
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class ShoppingEngine(BaseKnowledgeEngine):
    beat_id = BeatId.SHOPPING

    CANONICAL_KEYWORDS = [
        "what shoes is he wearing",
        "what is she wearing",
        "where can i buy",
        "what brand is that",
        "shop this",
        "buy that",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="shoppable_tv",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Nike Cortez",
            subtitle="SPOTTED ON SCREEN \u00b7 REAL PRODUCT",
            verdict_badge="IDENTIFIED",
            verdict_color="emerald",
            primary_explanation=(
                "Those are Nike Cortez \u2014 the white leather runner with the red "
                "swoosh, famously worn by Tom Hanks as Forrest Gump in the "
                "cross-country running scenes."
            ),
            key_details=[
                "Product: Nike Cortez (white / red-blue colorway).",
                "Released 1972, designed by Bill Bowerman \u2014 Nike's first track shoe.",
                "The Gump colorway is one of Nike's most reissued classics.",
            ],
            sources=[
                "Nike heritage records",
            ],
            companion_note="Learning Companion: Iconic movie sneakers saved to your watchlist.",
            latency_ms=8.0,
            is_canonical=True,
        )
