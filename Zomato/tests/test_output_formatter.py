"""
tests/test_output_formatter.py
───────────────────────────────
Unit tests for services/output_formatter.py.
Validates rank medals, currency formatting, rating strings, and match alignment scores.
"""

from models.restaurant import Recommendation
from services.output_formatter import format_recommendation, format_all


def test_format_recommendation_medals():
    """Verify correct medals for ranks 1, 2, 3 and numeric badges for 4+."""
    r1 = Recommendation(rank=1, name="Cafe 1", cuisine="cafe", rating=4.8, cost=600, explanation="test")
    r2 = Recommendation(rank=2, name="Cafe 2", cuisine="cafe", rating=4.5, cost=600, explanation="test")
    r3 = Recommendation(rank=3, name="Cafe 3", cuisine="cafe", rating=4.3, cost=600, explanation="test")
    r4 = Recommendation(rank=4, name="Cafe 4", cuisine="cafe", rating=4.1, cost=600, explanation="test")

    f1 = format_recommendation(r1)
    f2 = format_recommendation(r2)
    f3 = format_recommendation(r3)
    f4 = format_recommendation(r4)

    assert f1["medal"] == "🥇"
    assert f2["medal"] == "🥈"
    assert f3["medal"] == "🥉"
    assert f4["medal"] == "#4"


def test_format_recommendation_fields():
    """Verify strings and calculations are formatted as expected."""
    rec = Recommendation(
        rank=1,
        name="The Kind Roastery",
        cuisine="cafe, artisan bakery",
        rating=4.75,
        cost=950,
        explanation="Direct match for courtyard seating."
    )
    formatted = format_recommendation(rec)

    assert formatted["name"] == "The Kind Roastery"
    assert formatted["cuisine"] == "Cafe, Artisan Bakery"
    assert formatted["rating"] == 4.8
    assert formatted["rating_str"] == "4.8"
    assert formatted["cost"] == 950
    assert formatted["cost_str"] == "₹950 for two"
    assert formatted["match_score"] == 99.5


def test_format_all():
    """Verify format_all() converts list of Recommendations to list of dicts."""
    recs = [
        Recommendation(rank=1, name="R1", cuisine="c1", rating=4.5, cost=500, explanation="e1"),
        Recommendation(rank=2, name="R2", cuisine="c2", rating=4.2, cost=800, explanation="e2"),
    ]
    formatted = format_all(recs)
    assert len(formatted) == 2
    assert formatted[0]["name"] == "R1"
    assert formatted[1]["name"] == "R2"

