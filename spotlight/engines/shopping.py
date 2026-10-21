"""Beat 7 Knowledge Engine: Shoppable TV Moment.

Canonical Question: 'What shoes is he wearing?'
Target: Product card for the spotted item, clearly labeled demo catalog.
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
            title="Court Classic Sneaker — Sand/White",
            subtitle="SPOTTED ON SCREEN · DEMO CATALOG",
            verdict_badge="ADD TO CART",
            verdict_color="emerald",
            primary_explanation=(
                "Those are the Court Classic in Sand/White — full-grain leather, worn by the lead "
                "from minute 42 onward. This is a demo catalog entry: no real checkout, no real merchant."
            ),
            key_details=[
                "Product: Court Classic Sneaker, Sand/White.",
                "First spotted: 00:42:17, worn in 6 subsequent scenes.",
                "Demo catalog — prices and availability are illustrative only.",
            ],
            sources=[
                "SPOTLIGHT demo product catalog (fictional)",
            ],
            companion_note="Learning Companion: Shoppable moment saved to your watchlist.",
            latency_ms=8.0,
            is_canonical=True,
        )
