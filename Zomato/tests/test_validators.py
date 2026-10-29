"""
tests/test_validators.py
─────────────────────────
Unit tests for utils/validators.py.
Tests valid inputs and boundary/edge case validation.
"""

import pytest
from models.restaurant import UserPreferences
from utils.validators import validate_preferences


def test_valid_preferences():
    """Valid preferences must return an empty error list."""
    prefs = UserPreferences(
        location="Delhi",
        budget="medium",
        cuisines=["North Indian", "Chinese"],
        min_rating=4.0,
        extras="Good for families",
    )
    errors = validate_preferences(prefs)
    assert errors == []


@pytest.mark.parametrize("invalid_location", ["", "   ", None])
def test_missing_or_whitespace_location_fails(invalid_location):
    """Missing or whitespace-only location must generate an error."""
    prefs = UserPreferences(
        location=invalid_location,
        budget="low",
        cuisines=[],
        min_rating=3.5,
    )
    errors = validate_preferences(prefs)
    assert any("Location is required" in e for e in errors)


@pytest.mark.parametrize("invalid_budget", ["cheap", "expensive", "super-low", "", None])
def test_invalid_budget_fails(invalid_budget):
    """Budget values outside {'low', 'medium', 'high'} must generate an error."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=invalid_budget,
        cuisines=[],
        min_rating=4.0,
    )
    errors = validate_preferences(prefs)
    assert any("Budget must be one of" in e for e in errors)


@pytest.mark.parametrize("invalid_rating", [-0.5, 5.5, 10.0, -1.0])
def test_rating_out_of_range_fails(invalid_rating):
    """Ratings outside [0.0, 5.0] must generate an error."""
    prefs = UserPreferences(
        location="Mumbai",
        budget="high",
        cuisines=[],
        min_rating=invalid_rating,
    )
    errors = validate_preferences(prefs)
    assert any("Minimum rating must be between 0.0 and 5.0" in e for e in errors)


def test_excessive_extras_length_fails():
    """Extras exceeding 300 characters must generate an error."""
    prefs = UserPreferences(
        location="Delhi",
        budget="medium",
        cuisines=[],
        min_rating=4.0,
        extras="A" * 301,
    )
    errors = validate_preferences(prefs)
    assert any("Additional preferences must be under" in e for e in errors)

