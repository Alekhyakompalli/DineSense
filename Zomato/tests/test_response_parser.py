"""
tests/test_response_parser.py
──────────────────────────────
Unit tests for services/response_parser.py.
Validates clean parsing, markdown stripping, hallucination suppression,
missing field skipping, and malformed JSON detection.
"""

import pytest
from services.response_parser import parse_llm_response, _extract_json


@pytest.fixture
def candidate_names():
    return {"Spice Garden", "Pizza Hub", "Dragon Wok", "Brew Cafe"}


def test_parse_valid_json(candidate_names):
    """Clean JSON string must parse into valid Recommendation objects."""
    raw = """
    [
      {
        "rank": 1,
        "name": "Spice Garden",
        "cuisine": "North Indian",
        "rating": 4.5,
        "cost": 800,
        "explanation": "Authentic North Indian curries in a family-friendly setting."
      },
      {
        "rank": 2,
        "name": "Pizza Hub",
        "cuisine": "Italian",
        "rating": 4.2,
        "cost": 1100,
        "explanation": "Wood-fired pizzas that fit your medium budget perfectly."
      }
    ]
    """
    recs = parse_llm_response(raw, candidate_names)
    assert len(recs) == 2
    assert recs[0].name == "Spice Garden"
    assert recs[0].rank == 1
    assert recs[0].cost == 800
    assert recs[1].name == "Pizza Hub"


def test_parse_json_with_markdown_fence(candidate_names):
    """Markdown code fences (```json ... ```) must be stripped automatically."""
    raw = """
    ```json
    [
      {
        "rank": 1,
        "name": "Dragon Wok",
        "cuisine": "Chinese",
        "rating": 4.1,
        "cost": 700,
        "explanation": "Great Chinese food with rapid service."
      }
    ]
    ```
    """
    recs = parse_llm_response(raw, candidate_names)
    assert len(recs) == 1
    assert recs[0].name == "Dragon Wok"
    assert recs[0].cuisine == "Chinese"


def test_parse_rejects_hallucinated_restaurant(candidate_names):
    """Restaurants not present in candidate_names must be flagged and skipped."""
    raw = """
    [
      {
        "rank": 1,
        "name": "Fake Imaginary Bistro",
        "cuisine": "Continental",
        "rating": 4.9,
        "cost": 500,
        "explanation": "Hallucinated restaurant that was never in the candidate list."
      },
      {
        "rank": 2,
        "name": "Brew Cafe",
        "cuisine": "Cafe",
        "rating": 4.6,
        "cost": 400,
        "explanation": "Real cafe from candidate list."
      }
    ]
    """
    recs = parse_llm_response(raw, candidate_names)
    assert len(recs) == 1
    assert recs[0].name == "Brew Cafe"
    assert recs[0].rank == 2


def test_parse_raises_on_invalid_json(candidate_names):
    """Malformed non-JSON strings must raise a ValueError."""
    bad_raw = "Sorry, I am just an AI and I cannot recommend restaurants right now."
    with pytest.raises(ValueError, match="invalid JSON"):
        parse_llm_response(bad_raw, candidate_names)


def test_parse_skips_items_missing_fields(candidate_names):
    """Items missing required fields like 'rating' or 'explanation' must be skipped."""
    raw = """
    [
      {
        "rank": 1,
        "name": "Spice Garden"
        // Missing 'cuisine', 'rating', 'cost', 'explanation'
      },
      {
        "rank": 2,
        "name": "Pizza Hub",
        "cuisine": "Italian",
        "rating": 4.2,
        "cost": 1100,
        "explanation": "Complete item."
      }
    ]
    """
    # Fix comments to make JSON valid syntactically but with missing keys
    clean_raw = """
    [
      {
        "rank": 1,
        "name": "Spice Garden"
      },
      {
        "rank": 2,
        "name": "Pizza Hub",
        "cuisine": "Italian",
        "rating": 4.2,
        "cost": 1100,
        "explanation": "Complete item."
      }
    ]
    """
    recs = parse_llm_response(clean_raw, candidate_names)
    assert len(recs) == 1
    assert recs[0].name == "Pizza Hub"


def test_extract_json_helper():
    """Verify _extract_json strips both generic and language-tagged code fences."""
    raw_fence = "```\n[{\"test\": 1}]\n```"
    assert _extract_json(raw_fence) == '[{"test": 1}]'

    raw_json_fence = "```json\n[{\"test\": 2}]\n```"
    assert _extract_json(raw_json_fence) == '[{"test": 2}]'

    raw_empty = ""
    assert _extract_json(raw_empty) == ""
