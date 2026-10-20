"""Router and resolution orchestrator for the 4 Knowledge Engines and LLM Fallback."""

import time
from typing import Dict
from spotlight import config
from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.engines.kids import KidsEngine
from spotlight.engines.movie import MovieEngine
from spotlight.engines.news import NewsEngine
from spotlight.engines.sports import SportsEngine
from spotlight.engines.llm_fallback import llm_fallback_engine
from spotlight.models import AnswerPayload, BeatId, SceneData


class KnowledgeRouter:
    def __init__(self) -> None:
        self.engines: Dict[BeatId, BaseKnowledgeEngine] = {
            BeatId.KIDS: KidsEngine(),
            BeatId.MOVIE: MovieEngine(),
            BeatId.SPORTS: SportsEngine(),
            BeatId.NEWS: NewsEngine(),
        }

    async def resolve(
        self,
        beat_id: BeatId,
        question: str,
        custom_scene: SceneData | None = None,
        force_llm: bool = False,
    ) -> AnswerPayload:
        """Resolves a question using canonical curated engines or LLM fallback."""
        start_time = time.perf_counter()
        scene = custom_scene or config.SCENES.get(beat_id, config.SCENES[BeatId.KIDS])
        engine = self.engines.get(beat_id, self.engines[BeatId.KIDS])

        clean_question = question.strip() if question else scene.default_question

        # Curated answers ALWAYS win on canonical questions unless force_llm is requested
        if not force_llm and engine.can_handle_canonical(clean_question):
            answer = engine.get_canonical_answer(clean_question, scene)
            latency = (time.perf_counter() - start_time) * 1000.0
            answer.latency_ms = round(latency, 2)
            return answer

        # Otherwise route to LLM fallback
        answer = await llm_fallback_engine.generate_answer(clean_question, scene)
        return answer


# Global knowledge router instance
knowledge_router = KnowledgeRouter()
