"""
tests/conftest.py
──────────────────
Shared pytest fixtures for the full test suite.
"""

import pytest
import pandas as pd
from models.restaurant import Restaurant, UserPreferences, Recommendation


@pytest.fixture
def clean_df():
    """A minimal clean preprocessed DataFrame for filter/integration tests."""
    return pd.DataFrame({
        "name":     ["Spice Garden", "Curry House", "Pizza Hub", "Dragon Wok", "Brew Cafe"],
        "location": ["delhi",        "delhi",        "delhi",     "bangalore",  "bangalore"],
        "cuisines": ["north indian", "mughlai",      "italian",   "chinese",    "cafe"],
        "cost":     [800,            600,             1100,        700,          400],
        "budget":   ["medium",       "medium",        "medium",    "medium",     "low"],
        "rating":   [4.5,            4.2,             3.9,         4.1,          4.6],
    })


@pytest.fixture
def sample_restaurant():
    """A sample Restaurant dataclass instance."""
    return Restaurant(
        name="The Spice Route",
        location="delhi",
        cuisines="north indian, mughlai",
        cost=1200,
        budget="medium",
        rating=4.6,
    )


@pytest.fixture
def sample_preferences():
    """A sample UserPreferences dataclass instance."""
    return UserPreferences(
        location="delhi",
        budget="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
        extras="outdoor seating",
    )


@pytest.fixture
def sample_recommendation():
    """A sample Recommendation dataclass instance."""
    return Recommendation(
        rank=1,
        name="The Spice Route",
        cuisine="North Indian",
        rating=4.6,
        cost=1200,
        explanation="Renowned for exquisite North Indian delicacies and cozy ambience.",
    )
