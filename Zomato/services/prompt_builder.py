"""
services/prompt_builder.py
───────────────────────────
Constructs system and user prompts for the LLM recommendation engine.
Formats user preferences and serialized candidates into structured prompts.
"""

from models.restaurant import UserPreferences

SYSTEM_PROMPT = """You are an expert restaurant recommendation assistant.
Your job is to rank restaurants from the provided list based on the user's preferences.

Rules:
- ONLY recommend restaurants from the provided list. Do NOT invent or add restaurants.
- Return top restaurants ranked by best fit (up to 5, or all available if fewer than 5).
- For each restaurant, provide a concise explanation (1-2 sentences) of why it suits the user.
- Respond ONLY in valid JSON format — no markdown, no extra text, just the JSON array.
"""

USER_PROMPT_TEMPLATE = """User Preferences:
- Location: {location}
- Budget: {budget}
- Preferred Cuisines: {cuisines}
- Minimum Rating: {min_rating}
- Additional Notes: {extras}

Available Restaurants:
{candidates}

Return your top recommendations in this exact JSON format:
[
  {{
    "rank": 1,
    "name": "...",
    "cuisine": "...",
    "rating": 4.5,
    "cost": 800,
    "explanation": "..."
  }}
]
"""


def build_prompt(prefs: UserPreferences, serialized_candidates: str) -> tuple[str, str]:
    """
    Build system and user prompts for the LLM.

    Args:
        prefs: Validated user preferences.
        serialized_candidates: Numbered string of candidate restaurants.

    Returns:
        tuple[str, str]: (system_prompt, user_prompt)
    """
    cuisines_str = ", ".join(prefs.cuisines) if prefs.cuisines else "Any"
    extras_str = prefs.extras.strip() if prefs.extras and prefs.extras.strip() else "None"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        location=prefs.location,
        budget=prefs.budget.title() if prefs.budget else "Any",
        cuisines=cuisines_str,
        min_rating=prefs.min_rating,
        extras=extras_str,
        candidates=serialized_candidates if serialized_candidates else "None",
    )

    return SYSTEM_PROMPT, user_prompt
