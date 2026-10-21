"""Configuration and predefined scenes for Spotlight."""

import os
from typing import Dict
from spotlight.models import BeatId, SceneData

# Server config
HOST = os.getenv("SPOTLIGHT_HOST", "0.0.0.0")
PORT = int(os.getenv("SPOTLIGHT_PORT", "8000"))

# LLM Fallback config
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Predefined Scenes (Beat 1 to Beat 4)
SCENES: Dict[BeatId, SceneData] = {
    BeatId.KIDS: SceneData(
        beat_id=BeatId.KIDS,
        title="Planet Earthlings: Wonders of the Sky",
        channel="Discovery Horizon 4K",
        category="Science & Nature",
        timestamp="14:28",
        context_summary="A bright sunlit valley documentary segment explaining sunlight, rainbow refraction, and Earth's atmosphere.",
        default_question="Why is the sky blue?",
        visual_theme="nature-sky",
    ),
    BeatId.MOVIE: SceneData(
        beat_id=BeatId.MOVIE,
        title="The Syndicate Protocol",
        channel="Prime Cinema Premier",
        category="Espionage Thriller",
        timestamp="01:12:45",
        context_summary="Tense interrogation scene where Director Vance has just arrived at the underground compound after intercepting the cipher key.",
        default_question="Who is that guy and why is everyone mad at him?",
        visual_theme="cinema-noir",
    ),
    BeatId.SPORTS: SceneData(
        beat_id=BeatId.SPORTS,
        title="Intercontinental Champions Cup: Madrid vs Milan",
        channel="Sky Sports Matchday Live",
        category="International Soccer",
        timestamp="74:12",
        context_summary="A contentious sliding challenge at midfield where the referee has blown the whistle and players surround the referee.",
        default_question="Why was that a foul?",
        visual_theme="sports-pitch",
    ),
    BeatId.NEWS: SceneData(
        beat_id=BeatId.NEWS,
        title="Global Science Today: Space Exploration Archives",
        channel="World News Central HD",
        category="Journalism & Fact-Check",
        timestamp="09:15",
        context_summary="Broadcast segment addressing historical space milestones and pervasive misinformation regarding the 1969 Apollo lunar missions.",
        default_question="Is that claim true?",
        visual_theme="news-studio",
    ),
    BeatId.COOKING: SceneData(
        beat_id=BeatId.COOKING,
        title="Midnight Kitchen: Weeknight Shakshuka",
        channel="Sizzle Network 4K",
        category="Cooking Show",
        timestamp="22:41",
        context_summary="Chef blooms spices in hot oil before the tomatoes go in; the camera lingers on the spice tin.",
        default_question="What spice did they just add?",
        visual_theme="kitchen-warm",
    ),
    BeatId.ESPORTS: SceneData(
        beat_id=BeatId.ESPORTS,
        title="Grand Finals: Map 3 \u2014 Blue vs Red",
        channel="Arena Esports Live",
        category="Esports",
        timestamp="28:40",
        context_summary="Red team forces a 5v5 at mid lane right after blue spent ultimates on the dragon; blue wipes 0-for-4.",
        default_question="Why did they lose that fight?",
        visual_theme="arena-neon",
    ),
    BeatId.SHOPPING: SceneData(
        beat_id=BeatId.SHOPPING,
        title="The Last Heist \u2014 Rooftop Chase",
        channel="Prime Cinema Premier",
        category="Action / Shoppable",
        timestamp="00:42:17",
        context_summary="The lead sprints across rooftops; the camera holds on his sneakers for three full seconds.",
        default_question="What shoes is he wearing?",
        visual_theme="cinema-noir",
    ),
    BeatId.LANGUAGE: SceneData(
        beat_id=BeatId.LANGUAGE,
        title="Corazon Valiente S2E4",
        channel="Mundo Drama HD",
        category="Spanish Drama",
        timestamp="00:31:02",
        context_summary="A sister whispers encouragement to her brother before the final race; subtitles flash by quickly.",
        default_question="What did they just say?",
        visual_theme="drama-warm",
    ),
}

ORDERED_BEATS = [BeatId.KIDS, BeatId.MOVIE, BeatId.SPORTS, BeatId.NEWS, BeatId.COOKING, BeatId.ESPORTS, BeatId.SHOPPING, BeatId.LANGUAGE]
