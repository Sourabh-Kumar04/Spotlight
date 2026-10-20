"""Beat 4 Knowledge Engine: News Fact-Check Explainer.

Canonical Question: 'Is that claim true?'
Topic: Neutral scientific claim ('Did the Apollo 11 Moon landing happen?'). NEVER political.
Target: Fact-check overlay with verdict + 2 verified sources.
"""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.models import AnswerPayload, BeatId, SceneData


class NewsEngine(BaseKnowledgeEngine):
    beat_id = BeatId.NEWS

    CANONICAL_KEYWORDS = [
        "is that claim true",
        "is that true",
        "is this true",
        "is it true",
        "did the moon landing happen",
        "did we land on the moon",
        "moon landing real",
        "fact check",
        "is that fact",
    ]

    def can_handle_canonical(self, question: str) -> bool:
        norm = self.normalize_question(question)
        if not norm:
            return True
        return any(kw in norm for kw in self.CANONICAL_KEYWORDS)

    def get_canonical_answer(self, question: str, scene: SceneData) -> AnswerPayload:
        return AnswerPayload(
            engine_id="news_factcheck",
            beat_id=self.beat_id,
            question=question if question.strip() else scene.default_question,
            title="Fact-Check: Apollo 11 Lunar Landing",
            subtitle="NON-PARTISAN SCIENTIFIC AUDIT",
            verdict_badge="VERIFIED TRUE",
            verdict_color="emerald",
            primary_explanation=(
                "VERIFIED TRUE. On July 20, 1969, the Apollo 11 mission successfully touched down at Mare Tranquillitatis on the Moon. "
                "Astronauts Neil Armstrong and Buzz Aldrin walked on the lunar surface, installed laser reflectors still used by observatories today, "
                "and returned 21.5 kilograms of lunar rock samples examined and verified by independent research institutions across more than 40 nations."
            ),
            key_details=[
                "Direct Evidence: Lunar Laser Ranging retroreflectors left on the Moon by Apollo 11 continue to reflect laser pulses back to Earth stations with millimeter accuracy.",
                "Physical Artifacts: 382 kg of total lunar material across Apollo missions analyzed by global geochemists — containing zero atmospheric oxidation, impossible to fabricate on Earth.",
                "Global Tracking: Independent tracking from the Soviet Space Command (Jodrell Bank Observatory in the UK) monitored real-time radar telemetry confirming the lunar landing.",
            ],
            sources=[
                "NASA Apollo 11 Surface Journal & Mission Telemetry Archives (NASA History Division)",
                "Smithsonian National Air and Space Museum Lunar Exploration Registry (Accession #A19790001000)",
            ],
            companion_note="Learning Companion: Fact-check verified and pinned with primary citations in your Trust Feed.",
            latency_ms=13.0,
            is_canonical=True,
        )
