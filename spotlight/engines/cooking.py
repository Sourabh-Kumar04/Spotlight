"""Beat 5 Knowledge Engine: Cooking Show Ingredient Explainer.

Canonical Question: 'What spice did they just add?'
Target: Identify the ingredient/step and fold it into a running recipe.
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class CookingEngine(BaseKnowledgeEngine):
    beat_id = BeatId.COOKING

    CANONICAL_KEYWORDS = [
        "what spice did they just add",
        "what spice was that",
        "what ingredient",
        "what did they just add",
        "whats in the recipe",
        "recipe",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="cooking_show",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Smoked Paprika — Step 4 of 7",
            subtitle="RECIPE AUTO-BUILDER",
            verdict_badge="ADDED TO YOUR RECIPE",
            verdict_color="amber",
            primary_explanation=(
                "That was smoked paprika — one teaspoon, bloomed in the hot oil for 30 seconds "
                "before the tomatoes go in. Blooming wakes up the smoky flavor so it coats every bite."
            ),
            key_details=[
                "Ingredient: smoked paprika (pimentón), 1 tsp.",
                "Technique: bloom in oil 30s — never add to dry heat, it burns bitter.",
                "Running recipe so far: onion, garlic, cumin, smoked paprika.",
            ],
            sources=[
                "Show recipe card: Weeknight Shakshuka (demo kitchen)",
            ],
            companion_note="Learning Companion: Recipe step saved. 3 steps to a complete dish.",
            latency_ms=9.0,
            is_canonical=True,
        )
