"""
tests/test_filter.py
─────────────────────
Unit tests for services/filter_restaurants.py.
Validates location, budget, cuisine, rating constraints, capping,
fallback tiers, regex safety, and candidate serialization.
"""

import pytest
import pandas as pd
from models.restaurant import UserPreferences
from services.filter_restaurants import filter_restaurants, serialize_candidates


@pytest.fixture
def sample_df():
    """Clean minimal DataFrame for filter tests."""
    return pd.DataFrame({
        "name":     ["A", "B", "C", "D", "E"],
        "location": ["delhi", "delhi", "bangalore", "delhi", "delhi"],
        "cuisines": ["north indian", "italian", "chinese", "north indian", "mughlai"],
        "cost":     [400, 900, 600, 450, 1500],
        "budget":   ["low", "medium", "medium", "low", "high"],
        "rating":   [4.5, 4.0, 3.8, 3.5, 4.8],
    })


def make_prefs(**kwargs):
    """Helper to instantiate UserPreferences with sensible defaults."""
    defaults = dict(
        location="delhi",
        budget="low",
        cuisines=[],
        min_rating=0.0,
        extras=""
    )
    defaults.update(kwargs)
    return UserPreferences(**defaults)


def test_filter_by_location(sample_df):
    """Only restaurants matching the requested location substring should be returned."""
    result = filter_restaurants(sample_df, make_prefs(location="bangalore"))
    assert not result.empty
    assert all("bangalore" in loc for loc in result["location"])


def test_filter_by_budget(sample_df):
    """Strict filtering matches only the requested budget tier."""
    result = filter_restaurants(sample_df, make_prefs(location="delhi", budget="medium"))
    assert not result.empty
    assert result["budget"].eq("medium").all()


def test_filter_by_cuisine(sample_df):
    """Only restaurants serving one of the preferred cuisines are returned."""
    result = filter_restaurants(sample_df, make_prefs(location="delhi", budget="medium", cuisines=["Italian"]))
    assert not result.empty
    for row in result.itertuples():
        assert "italian" in row.cuisines.lower()


def test_filter_by_rating(sample_df):
    """No returned restaurant should have a rating below min_rating."""
    result = filter_restaurants(sample_df, make_prefs(location="delhi", min_rating=4.0))
    assert not result.empty
    assert (result["rating"] >= 4.0).all()


def test_filter_returns_no_more_than_top_n():
    """Result must never exceed TOP_N_CANDIDATES (20) even with large candidate pools."""
    large_df = pd.DataFrame({
        "name": [f"Restaurant {i}" for i in range(50)],
        "location": ["delhi"] * 50,
        "cuisines": ["north indian"] * 50,
        "cost": [400] * 50,
        "budget": ["low"] * 50,
        "rating": [4.0 + (i % 10) * 0.1 for i in range(50)],
    })
    result = filter_restaurants(large_df, make_prefs(location="delhi", budget="low"))
    assert len(result) <= 20


def test_sort_by_rating_descending(sample_df):
    """Candidates must be sorted monotonically descending by rating."""
    result = filter_restaurants(sample_df, make_prefs(location="delhi", budget="low"))
    ratings = result["rating"].tolist()
    assert ratings == sorted(ratings, reverse=True)


def test_unknown_location_returns_empty(sample_df):
    """Unknown location never matches and is not relaxed."""
    result = filter_restaurants(sample_df, make_prefs(location="nonexistent_city"))
    assert result.empty


def test_filter_fallback_relaxes_cuisine(sample_df):
    """When a cuisine has no matches in the location/budget, cuisine filter is relaxed."""
    # "Mexican" is not in sample_df for delhi/low -> falls back to relaxing cuisine
    result = filter_restaurants(
        sample_df,
        make_prefs(location="delhi", budget="low", cuisines=["Mexican"])
    )
    assert not result.empty
    assert result["budget"].eq("low").all()


def test_filter_fallback_relaxes_budget(sample_df):
    """When no restaurants match the budget tier, budget filter is relaxed (Level 2)."""
    # bangalore only has "medium" budget. Requesting "high" should relax budget to find it.
    result = filter_restaurants(
        sample_df,
        make_prefs(location="bangalore", budget="high", cuisines=[])
    )
    assert not result.empty
    assert "bangalore" in result.iloc[0]["location"]


def test_regex_special_chars_in_location_and_cuisine(sample_df):
    """Special regex metacharacters in location or cuisine strings must not cause re.error."""
    prefs = make_prefs(location="Delhi (NCR)+", cuisines=["Indian [Special]"])
    result = filter_restaurants(sample_df, prefs)
    assert isinstance(result, pd.DataFrame)


def test_serialize_candidates_format(sample_df):
    """Serialization produces a numbered string with name, location, cuisine, rating, cost, and budget."""
    serialized = serialize_candidates(sample_df.head(2))
    assert "1." in serialized
    assert "2." in serialized
    assert "Rating:" in serialized
    assert "Cost: ₹" in serialized
    assert "Budget:" in serialized


def test_serialize_candidates_empty():
    """Serializing an empty or None DataFrame returns an empty string."""
    assert serialize_candidates(pd.DataFrame()) == ""
    assert serialize_candidates(None) == ""


@pytest.mark.parametrize("location,budget,cuisines,min_rating,expect_empty", [
    ("delhi",      "low",    [],           0.0, False),
    ("delhi",      "low",    ["Italian"],  4.9, True),   # Exceeds max rating in dataset -> empty even with fallback
    ("xyzplace",   "low",    [],           0.0, True),   # Unknown location
    ("bangalore",  "high",   [],           0.0, False),  # Relaxed budget finds Bangalore
])
def test_parametric_filter(sample_df, location, budget, cuisines, min_rating, expect_empty):
    """Parametric evaluation across diverse constraint combinations."""
    prefs = make_prefs(
        location=location,
        budget=budget,
        cuisines=cuisines,
        min_rating=min_rating
    )
    result = filter_restaurants(sample_df, prefs)
    assert result.empty == expect_empty
