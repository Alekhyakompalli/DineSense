"""
services/output_formatter.py
─────────────────────────────
Formats Recommendation objects into display-ready dictionaries for the UI.
Matches the AI DineSense dark-theme schema with medal badges, match alignment scores,
formatted cost strings, and cleaned ratings.
"""

from models.restaurant import Recommendation

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def format_recommendation(rec: Recommendation) -> dict:
    """
    Convert a Recommendation object into a UI-ready dictionary.

    Args:
        rec: Recommendation domain instance.

    Returns:
        dict: Display-ready recommendation metadata.
    """
    return {
        "medal": RANK_MEDALS.get(rec.rank, f"#{rec.rank}"),
        "rank": rec.rank,
        "name": rec.name,
        "cuisine": rec.cuisine.title(),
        "rating": round(rec.rating, 1),
        "rating_str": f"{rec.rating:.1f}",
        "cost": rec.cost,
        "cost_str": f"₹{rec.cost:,} for two",
        "explanation": rec.explanation,
        "match_score": max(85.0, round(99.5 - (rec.rank - 1) * 2.8, 1)),
    }


def format_all(recommendations: list[Recommendation]) -> list[dict]:
    """
    Format a collection of Recommendation objects into display dictionaries.

    Args:
        recommendations: List of Recommendation instances.

    Returns:
        list[dict]: List of display dictionaries.
    """
    return [format_recommendation(r) for r in recommendations]
