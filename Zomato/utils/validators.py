"""
utils/validators.py
────────────────────
Input validation helpers for UserPreferences.
Ensures valid inputs before passing queries to the filtering and LLM layers.
"""

from models.restaurant import UserPreferences
from config.settings import MAX_EXTRAS_LENGTH

VALID_BUDGETS = {"low", "medium", "high"}


def validate_preferences(prefs: UserPreferences) -> list[str]:
    """
    Validate a UserPreferences instance.

    Checks:
    - Location: must be non-empty and non-whitespace string.
    - Budget: must be one of 'low', 'medium', 'high'.
    - Minimum rating: must be between 0.0 and 5.0.
    - Extras: length must not exceed MAX_EXTRAS_LENGTH characters.

    Args:
        prefs: UserPreferences dataclass instance to validate.

    Returns:
        list[str]: List of validation error messages. Empty list indicates valid inputs.
    """
    errors: list[str] = []

    # 1. Location validation
    if not prefs.location or not prefs.location.strip():
        errors.append("Location is required.")

    # 2. Budget validation
    if not prefs.budget or prefs.budget.lower().strip() not in VALID_BUDGETS:
        errors.append("Budget must be one of: low, medium, high.")

    # 3. Rating validation
    if prefs.min_rating is None or not (0.0 <= prefs.min_rating <= 5.0):
        errors.append("Minimum rating must be between 0.0 and 5.0.")

    # 4. Free-text extras length validation
    if prefs.extras and len(prefs.extras) > MAX_EXTRAS_LENGTH:
        errors.append(f"Additional preferences must be under {MAX_EXTRAS_LENGTH} characters.")

    return errors
