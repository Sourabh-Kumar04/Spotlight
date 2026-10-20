"""Unit tests for the LLM Fallback engine."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from spotlight import config
from spotlight.engines.llm_fallback import LLMFallbackEngine
from spotlight.models import BeatId


@pytest.mark.asyncio
async def test_llm_fallback_contextual_synthesis_when_offline():
    engine = LLMFallbackEngine()
    # Point to an offline unreachable host to force fallback to contextual synthesis
    engine.ollama_host = "http://127.0.0.1:54321"
    scene = config.SCENES[BeatId.KIDS]

    ans = await engine.generate_answer("How do birds fly in the sky?", scene, timeout=0.5)
    assert ans.is_canonical is False
    assert ans.engine_id == "contextual_synthesis"
    assert ans.verdict_badge == "READ ALOUD READY"
    assert len(ans.primary_explanation) > 20
    assert len(ans.key_details) >= 1
    assert len(ans.sources) >= 1


@pytest.mark.asyncio
async def test_llm_fallback_mocked_ollama_success():
    engine = LLMFallbackEngine()
    scene = config.SCENES[BeatId.SPORTS]

    mock_ollama_json = {
        "title": "Offside Rule Breakdown",
        "subtitle": "TACTICAL OFFICIATING REVIEW",
        "verdict_badge": "OFFSIDE FLAG UP",
        "verdict_color": "rose",
        "primary_explanation": "The forward was leaning past the second-last defender when the ball was kicked.",
        "key_details": ["Forward in active play position", "Interfered with goalkeeper sightline"],
        "sources": ["IFAB Law 11", "Match Analysis Room"],
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": json.dumps(mock_ollama_json)}

    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        ans = await engine.generate_answer("Was he offside?", scene)
        assert ans.is_canonical is False
        assert ans.engine_id == "llm_ollama"
        assert ans.title == "Offside Rule Breakdown"
        assert ans.verdict_badge == "OFFSIDE FLAG UP"
        assert ans.verdict_color == "rose"
        assert "IFAB Law 11" in ans.sources


@pytest.mark.asyncio
async def test_llm_fallback_mocked_openai_success():
    engine = LLMFallbackEngine()
    engine.openai_key = "test-key-12345"
    scene = config.SCENES[BeatId.MOVIE]

    mock_openai_json = {
        "title": "Safehouse Extraction Protocol",
        "subtitle": "PLOT CONTINUITY BRIEF",
        "verdict_badge": "CLASSIFIED INTEL",
        "verdict_color": "amber",
        "primary_explanation": "Vance managed to disable the elevator power grid before fleeing.",
        "key_details": ["Elevator locks engaged", "Team searching for alternate staircase"],
        "sources": ["Syndicate Production Dossier", "Scene 4 Continuity"],
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(mock_openai_json)}}]
    }

    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        ans = await engine.generate_answer("Where did he go?", scene)
        assert ans.is_canonical is False
        assert ans.engine_id == "llm_openai"
        assert ans.title == "Safehouse Extraction Protocol"
        assert ans.verdict_badge == "CLASSIFIED INTEL"


def test_llm_clean_and_parse_json_markdown():
    engine = LLMFallbackEngine()
    raw = "```json\n{\"title\": \"Test Headline\", \"verdict_badge\": \"TEST\"}\n```"
    parsed = engine._clean_and_parse_json(raw)
    assert parsed is not None
    assert parsed["title"] == "Test Headline"
    assert parsed["verdict_badge"] == "TEST"


def test_llm_clean_and_parse_json_invalid():
    engine = LLMFallbackEngine()
    assert engine._clean_and_parse_json("Not valid json at all") is None
