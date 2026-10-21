"""Beat 8 Knowledge Engine: Language Learning Companion.

Canonical Question: 'What did they just say?'
Target: Instant translation with context note (Spanish → English).
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class LanguageEngine(BaseKnowledgeEngine):
    beat_id = BeatId.LANGUAGE

    CANONICAL_KEYWORDS = [
        "what did they just say",
        "what does that mean",
        "translate",
        "what did she say",
        "what did he say",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="language_companion",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title='"No te rindas" — Don\'t give up',
            subtitle="SPANISH → ENGLISH · IN CONTEXT",
            verdict_badge="PHRASE SAVED",
            verdict_color="sky",
            primary_explanation=(
                '"No te rindas" — "Don\'t give up." She says it to her brother before the final race. '
                "Note the informal 'te': she'd use 'se' with a stranger. This is the encouragement form, "
                "not a command."
            ),
            key_details=[
                "Literal: 'Don't surrender yourself' → natural: 'Don't give up.'",
                "Register: informal (te) — family and friends, not formal settings.",
                "Saved to your phrasebook: 12 phrases this week.",
            ],
            sources=[
                "Episode subtitles: S2E4, 00:31:02 (demo program)",
            ],
            companion_note="Learning Companion: Phrase saved. Review at bedtime for retention.",
            latency_ms=10.0,
            is_canonical=True,
        )
