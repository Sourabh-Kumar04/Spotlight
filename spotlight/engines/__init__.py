"""Spotlight Knowledge Engines package."""

from spotlight.engines.base import BaseKnowledgeEngine
from spotlight.engines.kids import KidsEngine
from spotlight.engines.movie import MovieEngine
from spotlight.engines.sports import SportsEngine
from spotlight.engines.news import NewsEngine
from spotlight.engines.llm_fallback import LLMFallbackEngine, llm_fallback_engine
from spotlight.engines.router import KnowledgeRouter, knowledge_router

__all__ = [
    "BaseKnowledgeEngine",
    "KidsEngine",
    "MovieEngine",
    "SportsEngine",
    "NewsEngine",
    "LLMFallbackEngine",
    "llm_fallback_engine",
    "KnowledgeRouter",
    "knowledge_router",
]
