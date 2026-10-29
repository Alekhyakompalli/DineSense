"""
tests/test_prompt_builder.py
─────────────────────────────
Unit tests for services/prompt_builder.py.
Validates system prompt rules, preference insertion, candidate serialization,
and JSON format instructions.
"""

from models.restaurant import UserPreferences
from services.prompt_builder import build_prompt, SYSTEM_PROMPT


def test_build_prompt_system_prompt_not_empty():
    """System prompt must be non-empty and specify JSON rules."""
    prefs = UserPreferences(
        location="Delhi",
        budget="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
    )
    sys_prompt, _ = build_prompt(prefs, "1. Spice Garden | Rating: 4.5")
    assert sys_prompt.strip() != ""
    assert "JSON" in sys_prompt
    assert "ONLY recommend restaurants from the provided list" in sys_prompt


def test_build_prompt_contains_location():
    """User prompt must include the user's location."""
    prefs = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisines=[],
        min_rating=4.0,
    )
    _, user_prompt = build_prompt(prefs, "1. Truffles")
    assert "Koramangala" in user_prompt


def test_build_prompt_contains_cuisine():
    """User prompt must include the user's selected cuisines or 'Any'."""
    prefs = UserPreferences(
        location="Indiranagar",
        budget="low",
        cuisines=["Italian", "Cafe"],
        min_rating=3.5,
    )
    _, user_prompt = build_prompt(prefs, "1. Glen's Bakehouse")
    assert "Italian, Cafe" in user_prompt

    # Empty cuisines defaults to Any
    prefs_no_cuisine = UserPreferences(
        location="Indiranagar",
        budget="low",
        cuisines=[],
        min_rating=3.5,
    )
    _, user_prompt_any = build_prompt(prefs_no_cuisine, "1. Glen's Bakehouse")
    assert "Any" in user_prompt_any


def test_build_prompt_contains_candidates():
    """User prompt must contain the candidate restaurant string."""
    candidates_str = "1. Truffles | Rating: 4.7\n2. Lot Like Crepes | Rating: 4.7"
    prefs = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisines=[],
        min_rating=4.0,
    )
    _, user_prompt = build_prompt(prefs, candidates_str)
    assert "Truffles" in user_prompt
    assert "Lot Like Crepes" in user_prompt


def test_build_prompt_contains_extras():
    """User prompt must contain additional notes when provided."""
    prefs = UserPreferences(
        location="Whitefield",
        budget="high",
        cuisines=[],
        min_rating=4.5,
        extras="Romantic rooftop seating for an anniversary",
    )
    _, user_prompt = build_prompt(prefs, "1. Windmills Craftworks")
    assert "Romantic rooftop seating for an anniversary" in user_prompt


def test_build_prompt_contains_json_instruction():
    """User prompt must explicitly provide the expected JSON output format."""
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisines=[],
        min_rating=3.0,
    )
    _, user_prompt = build_prompt(prefs, "1. Saravana Bhavan")
    assert "exact JSON format" in user_prompt
    assert '"rank": 1' in user_prompt
    assert '"name":' in user_prompt
    assert '"explanation":' in user_prompt
