"""
services/filter_restaurants.py
────────────────────────────────
Structured filtering of the restaurant DataFrame based on user preferences.
Implements a 3-tier fallback strategy and candidate serialization for LLM prompts.
"""

import re
import pandas as pd
from models.restaurant import UserPreferences
from config.settings import TOP_N_CANDIDATES
from utils.logger import get_logger

logger = get_logger(__name__)


def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences) -> pd.DataFrame:
    """
    Filter restaurants by location, budget, cuisine, and rating.
    Applies a tiered fallback strategy if no results are found:
      1. Strict: location + budget + cuisine + rating
      2. Fallback 1: Relax cuisine (keep location, budget, rating)
      3. Fallback 2: Relax budget (keep location, rating)

    Args:
        df: Cleaned restaurant DataFrame.
        prefs: Validated UserPreferences object.

    Returns:
        pd.DataFrame: Up to TOP_N_CANDIDATES matching restaurants sorted by rating descending.
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame provided to filter_restaurants.")
        return pd.DataFrame()

    # Step 1: Strict filter
    result = _apply_filters(df, prefs, relax_cuisine=False, relax_budget=False)

    # Step 2: Fallback 1 — relax cuisine if cuisine was specified
    if result.empty and prefs.cuisines:
        logger.warning("No results found — relaxing cuisine filter (Fallback Level 1).")
        result = _apply_filters(df, prefs, relax_cuisine=True, relax_budget=False)

    # Step 3: Fallback 2 — relax budget if still no results
    if result.empty:
        logger.warning("Still no results — relaxing budget filter (Fallback Level 2).")
        result = _apply_filters(df, prefs, relax_cuisine=True, relax_budget=True)

    if result.empty:
        logger.warning("No matching restaurants found after all fallbacks.")

    return result


def _apply_filters(
    df: pd.DataFrame,
    prefs: UserPreferences,
    relax_cuisine: bool = False,
    relax_budget: bool = False,
) -> pd.DataFrame:
    """
    Apply individual filter predicates against the restaurant DataFrame.

    Args:
        df: Input DataFrame.
        prefs: UserPreferences criteria.
        relax_cuisine: If True, skips the cuisine filter.
        relax_budget: If True, skips the budget filter.

    Returns:
        pd.DataFrame: Filtered DataFrame subset.
    """
    filtered = df.copy()

    # 1. Location filter
    # If the user input contains a comma/city suffix (e.g. "Koramangala, Bangalore"),
    # match against full string or primary locality token before the comma.
    raw_loc = prefs.location.lower().strip()
    safe_location = re.escape(raw_loc)
    loc_match = filtered["location"].str.contains(safe_location, na=False)

    if not loc_match.any() and "," in raw_loc:
        primary_part = re.escape(raw_loc.split(",")[0].strip())
        if primary_part:
            loc_match = filtered["location"].str.contains(primary_part, na=False)

    filtered = filtered[loc_match]

    # 2. Budget filter
    if not relax_budget:
        budget_val = prefs.budget.lower().strip()
        filtered = filtered[filtered["budget"] == budget_val]

    # 3. Cuisine filter (if cuisines provided and not relaxed)
    if prefs.cuisines and not relax_cuisine:
        cuisine_patterns = [
            re.escape(c.lower().strip()) for c in prefs.cuisines if c.strip()
        ]
        if cuisine_patterns:
            pattern = "|".join(cuisine_patterns)
            filtered = filtered[filtered["cuisines"].str.contains(pattern, na=False)]

    # 4. Rating floor filter
    filtered = filtered[filtered["rating"] >= prefs.min_rating]

    # 5. Sort by rating descending and cap at TOP_N_CANDIDATES
    filtered = (
        filtered.sort_values(by="rating", ascending=False)
        .head(TOP_N_CANDIDATES)
        .reset_index(drop=True)
    )

    logger.info(
        f"Filter evaluated: {len(filtered)} candidates returned "
        f"(relax_cuisine={relax_cuisine}, relax_budget={relax_budget})"
    )
    return filtered


def serialize_candidates(df: pd.DataFrame) -> str:
    """
    Convert a candidate DataFrame into a structured, numbered string for LLM prompts.

    Args:
        df: Filtered candidate DataFrame.

    Returns:
        str: Serialized newline-separated candidate list.
    """
    if df is None or df.empty:
        return ""

    lines: list[str] = []
    for i, row in enumerate(df.itertuples(), start=1):
        lines.append(
            f"{i}. {row.name} | Location: {row.location} | "
            f"Cuisine: {row.cuisines} | Rating: {row.rating} | "
            f"Cost: ₹{row.cost} for two | Budget: {row.budget}"
        )
    return "\n".join(lines)
