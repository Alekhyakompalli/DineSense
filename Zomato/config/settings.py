"""
config/settings.py
──────────────────
Central configuration for the Zomato AI Recommendation System.
Loads all values from the .env file via python-dotenv.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ── Locate and load .env ──────────────────────────────────────────────────────
_env_path = Path(__file__).resolve().parent.parent / ".env"

if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    # On production platforms like Railway, env vars are injected directly
    load_dotenv()

# ── Python version guard ──────────────────────────────────────────────────────
if sys.version_info < (3, 10):
    raise RuntimeError(
        f"Python 3.10+ is required. You are running {sys.version}.\n"
        "Please upgrade your Python installation."
    )

# ── LLM Provider ─────────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

VALID_PROVIDERS = {"openai", "gemini", "huggingface"}
if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(
        f"[CONFIG ERROR] Unknown LLM_PROVIDER: '{LLM_PROVIDER}'.\n"
        f"  Valid options: {VALID_PROVIDERS}\n"
        "  Check your .env file."
    )

# ── API Keys & Models ─────────────────────────────────────────────────────────
OPENAI_API_KEY:    str | None = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY:    str | None = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
HUGGINGFACE_TOKEN: str | None = os.getenv("HUGGINGFACE_TOKEN")

GEMINI_MODEL:      str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL:      str = os.getenv("OPENAI_MODEL", "gpt-4o")

# Validate the active provider has a key
_key_map = {
    "openai":       ("OPENAI_API_KEY",    OPENAI_API_KEY),
    "gemini":       ("GOOGLE_API_KEY",    GOOGLE_API_KEY),
    "huggingface":  ("HUGGINGFACE_TOKEN", HUGGINGFACE_TOKEN),
}
_key_name, _key_value = _key_map[LLM_PROVIDER]
if not _key_value:
    raise EnvironmentError(
        f"\n[CONFIG ERROR] '{_key_name}' (or GEMINI_API_KEY) is not set in your .env file.\n"
        f"  The selected LLM provider is '{LLM_PROVIDER}'.\n"
        "  Add your API key to .env and restart.\n"
    )

# ── Recommendation Settings ───────────────────────────────────────────────────
TOP_N_CANDIDATES:      int = int(os.getenv("TOP_N_CANDIDATES",      "20"))
TOP_N_RECOMMENDATIONS: int = int(os.getenv("TOP_N_RECOMMENDATIONS", "5"))
MAX_EXTRAS_LENGTH:     int = 300   # Max characters for free-text extras field

# ── Budget Mapping ────────────────────────────────────────────────────────────
# Maps budget tier names to INR cost ranges (approx cost for two people)
BUDGET_MAP: dict[str, tuple[int, int]] = {
    "low":    (0,    500),
    "medium": (501,  1200),
    "high":   (1201, 99999),
}

# ── Dataset ───────────────────────────────────────────────────────────────────
DATASET_NAME: str = os.getenv("DATASET_NAME", "ManikaSaini/zomato-restaurant-recommendation")

