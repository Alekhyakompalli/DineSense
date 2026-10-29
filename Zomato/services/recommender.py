"""
services/recommender.py
────────────────────────
Orchestrates the full restaurant recommendation pipeline:
  1. Filter candidates based on UserPreferences with 3-tier fallback.
  2. Serialize candidates for prompt ingestion.
  3. Build system and user prompts.
  4. Query LLM via LLMClient with retry/backoff.
  5. Parse and validate JSON response, verifying against hallucinations.
  6. Retry with stricter prompt on JSON parse failure; fallback to candidates if all fails.
"""

import pandas as pd
from models.restaurant import UserPreferences, Recommendation
from services.filter_restaurants import filter_restaurants, serialize_candidates
from services.prompt_builder import build_prompt
from services.llm_client import LLMClient
from services.response_parser import parse_llm_response
from utils.logger import get_logger

logger = get_logger(__name__)

_global_client: LLMClient | None = None


def get_default_llm_client() -> LLMClient:
    """Retrieve or lazily instantiate the shared LLMClient instance."""
    global _global_client
    if _global_client is None:
        _global_client = LLMClient()
    return _global_client


def get_recommendations(
    df: pd.DataFrame,
    prefs: UserPreferences,
    client: LLMClient | None = None,
) -> list[Recommendation]:
    """
    Run end-to-end recommendation workflow with robust error handling and fallback.

    Args:
        df: Cleaned restaurant DataFrame.
        prefs: Validated user preferences.
        client: Optional LLMClient instance (defaults to shared client).

    Returns:
        list[Recommendation]: Ordered list of recommendations with rank and explanation.
    """
    # ── Step 1: Filter candidate restaurants ──────────────────────────────────
    candidates = filter_restaurants(df, prefs)
    if candidates.empty:
        logger.warning(f"No candidates found for preferences in location: '{prefs.location}'.")
        return []

    # ── Step 2: Serialize candidate pool ──────────────────────────────────────
    serialized = serialize_candidates(candidates)
    candidate_names = set(candidates["name"].tolist())
    logger.info(f"Passing {len(candidate_names)} candidates to LLM prompt.")

    # ── Step 3: Build prompts ─────────────────────────────────────────────────
    system_prompt, user_prompt = build_prompt(prefs, serialized)

    # ── Step 4: Call LLM with retry & stricter prompt on parse failure ───────
    llm = client or get_default_llm_client()
    recommendations: list[Recommendation] = []

    try:
        raw_response = llm.complete(system_prompt, user_prompt)
        recommendations = parse_llm_response(raw_response, candidate_names)
    except ValueError as parse_err:
        logger.warning(f"Initial JSON parse failed: {parse_err}. Retrying with stricter prompt...")
        try:
            strict_system = (
                system_prompt
                + "\nCRITICAL RULE: Respond ONLY with a valid JSON array. "
                "Do NOT include markdown formatting, code fences, or conversational text."
            )
            strict_response = llm.complete(strict_system, user_prompt)
            recommendations = parse_llm_response(strict_response, candidate_names)
        except Exception as retry_err:
            logger.error(f"Retry with strict prompt failed: {retry_err}.")
            recommendations = []
    except Exception as llm_err:
        logger.error(f"LLM API completion failed: {llm_err}. Using candidate ranking fallback.")
        recommendations = []

    # ── Step 5: Fallback Heuristic ─────────────────────────────────────────────
    # If the LLM returned 0 recommendations (due to parse error, API timeout, or hallucinations),
    # generate top recommendations directly from top candidates
    if not recommendations and not candidates.empty:
        logger.warning(
            "Generating fallback recommendations directly from top candidate records."
        )
        top_candidates = candidates.head(5)
        for rank, row in enumerate(top_candidates.itertuples(), start=1):
            recommendations.append(
                Recommendation(
                    rank=rank,
                    name=row.name,
                    cuisine=row.cuisines.title(),
                    rating=float(row.rating),
                    cost=int(row.cost),
                    explanation=(
                        f"Top-rated {row.budget} budget match in {row.location.title()} "
                        f"with a {row.rating}★ rating."
                    ),
                )
            )

    return recommendations
