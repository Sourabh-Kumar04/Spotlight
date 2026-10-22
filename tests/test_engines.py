"""Unit tests for the 4 Knowledge Engines in Spotlight."""

import pytest
from spotlight import config
from spotlight.engines.kids import KidsEngine
from spotlight.engines.movie import MovieEngine
from spotlight.engines.news import NewsEngine
from spotlight.engines.sports import SportsEngine
from spotlight.engines.router import knowledge_router
from spotlight.models import BeatId


def test_kids_engine_canonical_matching():
    engine = KidsEngine()
    scene = config.SCENES[BeatId.KIDS]

    assert engine.can_handle_canonical("Why is the sky blue?") is True
    assert engine.can_handle_canonical("why sky blue") is True
    assert engine.can_handle_canonical("What makes the sky blue?") is True
    assert engine.can_handle_canonical("") is True
    assert engine.can_handle_canonical("How do airplanes fly?") is False

    ans = engine.get_canonical_answer("Why is the sky blue?", scene)
    assert ans.is_canonical is True
    assert ans.verdict_badge == "PARENT READ-ALOUD READY"
    assert "Sunlight looks white to us" in ans.primary_explanation
    assert "Rayleigh scattering" in " ".join(ans.key_details)
    assert len(ans.sources) == 2
    assert ans.latency_ms < 100.0


def test_movie_engine_canonical_matching():
    engine = MovieEngine()
    scene = config.SCENES[BeatId.MOVIE]

    assert engine.can_handle_canonical("Who is that guy and why is everyone mad at him?") is True
    assert engine.can_handle_canonical("who is that guy") is True
    assert engine.can_handle_canonical("who is that man") is True
    assert engine.can_handle_canonical("catch up") is True
    assert engine.can_handle_canonical("What is the recipe for pasta?") is False

    ans = engine.get_canonical_answer("who is that man?", scene)
    assert ans.is_canonical is True
    assert ans.title == "Cary Grant"
    assert ans.verdict_badge == "CAST SPOTLIGHT"
    assert "Cary Grant" in ans.primary_explanation
    assert "Peter Joshua" in ans.primary_explanation
    assert "Charade" in ans.key_details[0]
    assert len(ans.sources) >= 2


def test_sports_engine_canonical_matching():
    engine = SportsEngine()
    scene = config.SCENES[BeatId.SPORTS]

    assert engine.can_handle_canonical("Why was that a foul?") is True
    assert engine.can_handle_canonical("why foul") is True
    assert engine.can_handle_canonical("was that a foul") is True
    assert engine.can_handle_canonical("Who scored the touchdown?") is False

    ans = engine.get_canonical_answer("Why was that a foul?", scene)
    assert ans.is_canonical is True
    assert ans.verdict_badge == "DIRECT FREE KICK + YELLOW CARD"
    assert "74:12" in ans.primary_explanation
    assert "IFAB Law 12" in " ".join(ans.key_details)
    assert "Yellow Card" in " ".join(ans.key_details)
    assert len(ans.sources) >= 2


def test_news_engine_canonical_matching():
    engine = NewsEngine()
    scene = config.SCENES[BeatId.NEWS]

    assert engine.can_handle_canonical("Is that claim true?") is True
    assert engine.can_handle_canonical("did the moon landing happen") is True
    assert engine.can_handle_canonical("moon landing real") is True
    assert engine.can_handle_canonical("What is tomorrow's weather?") is False

    ans = engine.get_canonical_answer("Is that claim true?", scene)
    assert ans.is_canonical is True
    assert ans.verdict_badge == "VERIFIED TRUE"
    assert "Apollo 11" in ans.primary_explanation
    assert "July 20, 1969" in ans.primary_explanation
    assert len(ans.sources) >= 2
    assert any("NASA" in src for src in ans.sources)


@pytest.mark.asyncio
async def test_knowledge_router_canonical_resolution():
    # Canonical queries always win and resolve with sub-100ms latency
    ans1 = await knowledge_router.resolve(BeatId.KIDS, "Why is the sky blue?")
    assert ans1.is_canonical is True
    assert ans1.latency_ms < 100.0

    ans2 = await knowledge_router.resolve(BeatId.MOVIE, "Who is that guy and why is everyone mad at him?")
    assert ans2.is_canonical is True
    assert ans2.latency_ms < 100.0

    ans3 = await knowledge_router.resolve(BeatId.SPORTS, "Why was that a foul?")
    assert ans3.is_canonical is True
    assert ans3.latency_ms < 100.0

    ans4 = await knowledge_router.resolve(BeatId.NEWS, "Is that claim true?")
    assert ans4.is_canonical is True
    assert ans4.latency_ms < 100.0
