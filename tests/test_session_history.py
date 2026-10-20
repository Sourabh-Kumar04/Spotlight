"""Unit tests for Session History & Learning Companion seed engine."""

import pytest
from spotlight.models import BeatId
from spotlight.session import SessionManager


def test_session_manager_initial_state():
    mgr = SessionManager()
    assert len(mgr.history) == 0
    stats = mgr.get_stats()
    assert stats["total_questions"] == 0
    assert stats["canonical_answers"] == 0


def test_session_manager_record_canonical_ask():
    mgr = SessionManager()
    item = mgr.record_ask(
        beat_id=BeatId.KIDS,
        category="Science & Nature",
        question="Why is the sky blue?",
        answer_title="Why the Sky Is Blue",
        is_canonical=True,
        latency_ms=12.5,
    )
    assert item.beat_id == BeatId.KIDS
    assert item.category == "Science & Nature"
    assert "Family Curiosity Journal" in item.companion_note
    assert len(mgr.history) == 1
    assert mgr.get_stats()["canonical_answers"] == 1


def test_session_manager_foul_recurrence_companion_note():
    mgr = SessionManager()

    # First soccer foul inquiry
    item1 = mgr.record_ask(
        beat_id=BeatId.SPORTS,
        category="International Soccer",
        question="Why was that a foul?",
        answer_title="Match Official Decision",
        is_canonical=True,
        latency_ms=10.0,
    )
    assert "First soccer rule logged" in item1.companion_note

    # Second soccer foul inquiry — triggers recurrence prompt
    item2 = mgr.record_ask(
        beat_id=BeatId.SPORTS,
        category="International Soccer",
        question="Why was that a foul?",
        answer_title="Match Official Decision",
        is_canonical=True,
        latency_ms=9.8,
    )
    assert "You've asked about fouls twice this week" in item2.companion_note
    assert mgr.topic_counts["fouls"] == 2


def test_session_manager_movie_companion_note():
    mgr = SessionManager()
    item = mgr.record_ask(
        beat_id=BeatId.MOVIE,
        category="Espionage Thriller",
        question="Who is that guy and why is everyone mad at him?",
        answer_title="Catch-Up Card: Director Vance",
        is_canonical=True,
        latency_ms=14.0,
    )
    assert "Living Cast card" in item.companion_note


def test_session_manager_news_companion_note():
    mgr = SessionManager()
    item = mgr.record_ask(
        beat_id=BeatId.NEWS,
        category="Journalism & Fact-Check",
        question="Is that claim true?",
        answer_title="Fact-Check: Apollo 11",
        is_canonical=True,
        latency_ms=13.0,
    )
    assert "Trust Feed" in item.companion_note


def test_session_manager_history_ordering():
    mgr = SessionManager()
    mgr.record_ask(BeatId.KIDS, "Science", "Q1", "A1", True, 10.0)
    mgr.record_ask(BeatId.MOVIE, "Movie", "Q2", "A2", True, 10.0)
    mgr.record_ask(BeatId.SPORTS, "Sports", "Q3", "A3", True, 10.0)

    history = mgr.get_history()
    # Most recent first
    assert history[0].question == "Q3"
    assert history[1].question == "Q2"
    assert history[2].question == "Q1"


def test_session_manager_clear():
    mgr = SessionManager()
    mgr.record_ask(BeatId.KIDS, "Science", "Q1", "A1", True, 10.0)
    mgr.clear()
    assert len(mgr.history) == 0
    assert mgr.topic_counts["fouls"] == 0
    assert mgr.topic_counts["sky"] == 0
