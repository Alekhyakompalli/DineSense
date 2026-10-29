"""
tests/test_recommender.py
─────────────────────────
Unit tests for services/recommender.py.
Tests end-to-end orchestration, retry on malformed JSON, and fallback to candidates.
"""

from unittest.mock import MagicMock
import pandas as pd
from models.restaurant import UserPreferences
from services.recommender import get_recommendations


def test_get_recommendations_pipeline(clean_df):
    """Verify that get_recommendations coordinates filtering, prompting, LLM call, and parsing."""
    prefs = UserPreferences(
        location="delhi",
        budget="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
        extras="family dinner",
    )

    mock_llm_response = """
    [
      {
        "rank": 1,
        "name": "Spice Garden",
        "cuisine": "North Indian",
        "rating": 4.5,
        "cost": 800,
        "explanation": "Top-rated North Indian restaurant in Delhi fitting your budget and family outing."
      }
    ]
    """

    mock_client = MagicMock()
    mock_client.complete.return_value = mock_llm_response

    recs = get_recommendations(clean_df, prefs, client=mock_client)

    assert len(recs) == 1
    assert recs[0].rank == 1
    assert recs[0].name == "Spice Garden"
    assert recs[0].rating == 4.5
    assert "family" in recs[0].explanation.lower()

    # Ensure client was called with system and user prompts
    mock_client.complete.assert_called_once()
    args, _ = mock_client.complete.call_args
    system_prompt, user_prompt = args
    assert "expert restaurant recommendation" in system_prompt.lower()
    assert "delhi" in user_prompt.lower()
    assert "Spice Garden" in user_prompt


def test_get_recommendations_empty_when_no_candidates(clean_df):
    """When candidates DataFrame is empty (unknown location), return empty list without calling LLM."""
    prefs = UserPreferences(
        location="unknown_city_xyz",
        budget="medium",
        cuisines=[],
        min_rating=4.0,
    )
    mock_client = MagicMock()
    recs = get_recommendations(clean_df, prefs, client=mock_client)
    assert recs == []
    mock_client.complete.assert_not_called()


def test_get_recommendations_retries_on_malformed_json(clean_df):
    """When initial response is malformed, retry with stricter prompt and succeed."""
    prefs = UserPreferences(
        location="delhi",
        budget="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
    )

    valid_response = """
    [
      {
        "rank": 1,
        "name": "Spice Garden",
        "cuisine": "North Indian",
        "rating": 4.5,
        "cost": 800,
        "explanation": "Delicious curries."
      }
    ]
    """

    mock_client = MagicMock()
    # First call returns invalid JSON, second call returns valid JSON
    mock_client.complete.side_effect = ["NOT VALID JSON {{{{", valid_response]

    recs = get_recommendations(clean_df, prefs, client=mock_client)

    assert len(recs) == 1
    assert recs[0].name == "Spice Garden"
    assert mock_client.complete.call_count == 2


def test_get_recommendations_fallback_on_persistent_failure(clean_df):
    """When LLM repeatedly fails or returns invalid output, generate fallback from top candidates."""
    prefs = UserPreferences(
        location="delhi",
        budget="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
    )

    mock_client = MagicMock()
    mock_client.complete.side_effect = RuntimeError("API unavailable")

    recs = get_recommendations(clean_df, prefs, client=mock_client)

    # Should not raise; instead return candidates fallback
    assert len(recs) > 0
    assert recs[0].rank == 1
    assert "Spice Garden" in [r.name for r in recs]
    assert "Top-rated" in recs[0].explanation
