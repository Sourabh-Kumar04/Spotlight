"""Beat 1 Knowledge Engine: Kids Documentary Explainer.

Canonical Question: 'Why is the sky blue?'
Target: Simple, warm explanation a parent can read aloud (2-3 sentences, kid-friendly).
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class KidsEngine(BaseKnowledgeEngine):
    beat_id = BeatId.KIDS

    CANONICAL_KEYWORDS = [
        "why is the sky blue",
        "why the sky is blue",
        "why is sky blue",
        "why sky blue",
        "sky blue",
        "what makes the sky blue",
        "how come the sky is blue",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True  # default question
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="kids_documentary",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Why the Sky Is Blue",
            subtitle="READ-ALOUD FAMILY EXPLAINER",
            verdict_badge="PARENT READ-ALOUD READY",
            verdict_color="sky",
            primary_explanation=(
                "Sunlight looks white to us, but it is secretly made of all the colors of the rainbow packed together! "
                "When sunlight reaches Earth, tiny particles in our air bump into the blue light and scatter it in every direction across the sky. "
                "Because blue light bounces around more than other colors, the whole sky glows with that beautiful bright blue blanket for us to enjoy!"
            ),
            key_details=[
                "Sunlight is made of all rainbow colors travelling together.",
                "Blue light travels in short, smaller waves that bounce easily off air particles.",
                "Scientists call this gentle bouncing 'Rayleigh scattering'.",
            ],
            sources=[
                "NASA Science Space Place: Atmospheric Scattering Guide",
                "Discovery Horizon Earth Systems Curriculum (Ages 6-12)",
            ],
            companion_note="Learning Companion: Science question logged to Family Curiosity Journal. Great follow-up for bedtime reading.",
            latency_ms=12.0,
            is_canonical=True,
        )
