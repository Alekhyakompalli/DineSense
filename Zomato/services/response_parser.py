"""
services/response_parser.py
────────────────────────────
Parses and validates raw LLM JSON responses into Recommendation objects.
Includes hallucination detection against candidate names and robust field validation.
"""

import json
import re
from models.restaurant import Recommendation
from utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = {"rank", "name", "cuisine", "rating", "cost", "explanation"}


def _extract_json(raw: str) -> str:
    """
    Extract clean JSON string from raw LLM output, stripping markdown fences if present.

    Args:
        raw: Raw text output from the LLM.

    Returns:
        str: Clean JSON substring.
    """
    if not raw:
        return ""

    # Check for markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    # Search for an array block [ ... ]
    array_match = re.search(r"\[[\s\S]*\]", raw)
    if array_match:
        return array_match.group(0).strip()

    return raw.strip()


def parse_llm_response(raw: str, candidate_names: set[str]) -> list[Recommendation]:
    """
    Parse and validate LLM JSON response into Recommendation objects.
    Performs hallucination check against the provided set of candidate restaurant names.

    Args:
        raw: Raw string response from the LLM.
        candidate_names: Set of restaurant names present in the filtered candidate set.

    Returns:
        list[Recommendation]: Validated, ranked recommendation objects.

    Raises:
        ValueError: If JSON is malformed or cannot be decoded.
    """
    json_str = _extract_json(raw)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}\nRaw output: {raw}")
        raise ValueError(f"LLM returned invalid JSON: {e}") from e

    if not isinstance(data, list):
        # In case the LLM returned a single dict wrapped in an object
        if isinstance(data, dict):
            # Check if there is an array under a key like 'recommendations'
            for key in ["recommendations", "restaurants", "results"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                data = [data]
        else:
            raise ValueError(f"Expected JSON array, got: {type(data).__name__}")

    # Canonical lowercase mapping for hallucination check
    canonical_candidates_map = {name.strip().lower(): name for name in candidate_names}

    recommendations: list[Recommendation] = []
    for item in data:
        if not isinstance(item, dict):
            logger.warning(f"Skipping non-dict recommendation item: {item}")
            continue

        # Validate required fields
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            logger.warning(f"Skipping item missing required fields {missing}: {item}")
            continue

        raw_name = str(item["name"]).strip()
        raw_name_lower = raw_name.lower()

        # Hallucination check against candidate pool
        if raw_name_lower not in canonical_candidates_map:
            logger.warning(
                f"Hallucinated restaurant skipped: '{raw_name}' not in candidate pool."
            )
            continue

        # Use canonical name from candidate list to avoid casing inconsistencies
        canonical_name = canonical_candidates_map[raw_name_lower]

        try:
            rank = int(item["rank"])
            cuisine = str(item["cuisine"]).strip()
            rating = float(item["rating"])
            cost = int(float(item["cost"]))  # Handles both 800 and 800.0
            explanation = str(item["explanation"]).strip()
        except (ValueError, TypeError) as cast_err:
            logger.warning(f"Skipping item due to type casting error ({cast_err}): {item}")
            continue

        recommendations.append(
            Recommendation(
                rank=rank,
                name=canonical_name,
                cuisine=cuisine,
                rating=rating,
                cost=cost,
                explanation=explanation,
            )
        )

    recommendations.sort(key=lambda r: r.rank)
    logger.info(f"Parsed {len(recommendations)} valid recommendations.")
    return recommendations
