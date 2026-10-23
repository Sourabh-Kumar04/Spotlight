"""Router and resolution orchestrator for the 4 Knowledge Engines and LLM Fallback."""

import time
from typing import Dict, Optional
from spotlight import config
from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.engines.kids import KidsEngine
from spotlight.engines.movie import MovieEngine
from spotlight.engines.news import NewsEngine
from spotlight.engines.sports import SportsEngine
from spotlight.engines.cooking import CookingEngine
from spotlight.engines.esports import EsportsEngine
from spotlight.engines.shopping import ShoppingEngine
from spotlight.engines.language import LanguageEngine
from spotlight.engines.llm_fallback import llm_fallback_engine
from spotlight.models import AnswerPayload, BeatId, SceneData
from spotlight.i18n import translate_answer


class KnowledgeRouter:
    def __init__(self) -> None:
        self.engines: Dict[BeatId, BaseKnowledgeEngine] = {
            BeatId.KIDS: KidsEngine(),
            BeatId.MOVIE: MovieEngine(),
            BeatId.SPORTS: SportsEngine(),
            BeatId.NEWS: NewsEngine(),
            BeatId.COOKING: CookingEngine(),
            BeatId.ESPORTS: EsportsEngine(),
            BeatId.SHOPPING: ShoppingEngine(),
            BeatId.LANGUAGE: LanguageEngine(),
        }

    async def resolve(
        self,
        beat_id: BeatId,
        question: str,
        custom_scene: SceneData | None = None,
        force_llm: bool = False,
        lang: str = "en",
        context_title: str | None = None,
        frame_b64: str | None = None,
        current_time: str | None = None,
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

        # Vision path: when frame_b64 is present and no canonical engine claimed the question
        if frame_b64:
            return await self._resolve_vision(
                clean_question,
                scene,
                frame_b64,
                context_title=context_title,
                start_time=start_time,
                current_time=current_time,
            )

        # Otherwise route to LLM fallback
        answer = await llm_fallback_engine.generate_answer(
            clean_question, scene, context_title=context_title, current_time=current_time
        )
        return answer

    async def _resolve_vision(
        self,
        question: str,
        scene: SceneData,
        frame_b64: str,
        context_title: Optional[str] = None,
        start_time: Optional[float] = None,
        current_time: Optional[str] = None,
    ) -> AnswerPayload:
        if start_time is None:
            start_time = time.perf_counter()

        import base64
        from spotlight.vision import analyze_frame

        raw_b64 = frame_b64.strip()
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(raw_b64)
        except Exception:
            image_bytes = b""

        if not image_bytes:
            # Invalid image base64; fall through to standard LLM fallback
            return await llm_fallback_engine.generate_answer(
                question, scene, context_title=context_title
            )

        vision_data = analyze_frame(image_bytes, question=question)
        answer = await llm_fallback_engine.generate_vision_answer(
            question, scene, vision_data, context_title=context_title
        )
        latency = (time.perf_counter() - start_time) * 1000.0
        answer.latency_ms = round(latency, 2)
        return answer

    async def resolve_localized(
        self,
        beat_id: BeatId,
        question: str,
        custom_scene: SceneData | None = None,
        force_llm: bool = False,
        lang: str = "en",
        context_title: str | None = None,
        frame_b64: str | None = None,
        current_time: str | None = None,
    ) -> AnswerPayload:
        """Resolve then translate canonical answers to the requested language."""
        answer = await self.resolve(
            beat_id,
            question,
            custom_scene,
            force_llm,
            lang,
            context_title=context_title,
            frame_b64=frame_b64,
            current_time=current_time,
        )
        return translate_answer(answer, lang)


# Global knowledge router instance
knowledge_router = KnowledgeRouter()
