"""
data/preprocessor.py
─────────────────────
Cleans, normalizes, and type-casts the raw Zomato DataFrame.
Executes a 7-step defensive preprocessing pipeline:
1. Column Selection & Validation
2. Column Renaming
3. Robust Type Casting (cost & rating)
4. Null Value Handling
5. Cost Normalization (Budget Tier Mapping)
6. Text Normalization (lowercase, strip whitespace)
7. Deduplication (keeping highest-rated duplicate)
"""

import pandas as pd
from config.settings import BUDGET_MAP
from utils.logger import get_logger

logger = get_logger(__name__)

# Canonical column definitions
RAW_COST_COL = "approx_cost(for two people)"
RAW_RATING_COL = "rate"
REQUIRED_CORE_COLS = ["name", "location", "cuisines"]


def map_budget(cost: int) -> str:
    """
    Map an integer cost (in INR for two) to a budget tier: 'low', 'medium', or 'high'.

    Args:
        cost: Estimated cost for two people.

    Returns:
        str: 'low' | 'medium' | 'high'
    """
    for tier, (low, high) in BUDGET_MAP.items():
        if low <= cost <= high:
            return tier
    return "high"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, validate, and normalize a raw Zomato DataFrame.

    Args:
        df: Raw DataFrame loaded from HuggingFace or CSV.

    Returns:
        pd.DataFrame: Cleaned DataFrame with schema:
            ['name', 'location', 'cuisines', 'cost', 'budget', 'rating']

    Raises:
        ValueError: If required columns are absent.
        RuntimeError: If DataFrame is empty after preprocessing.
    """
    if df is None or df.empty:
        raise RuntimeError("DataFrame is empty before preprocessing. Check the dataset.")

    df = df.copy()

    # ── Step 1: Validate required core columns ────────────────────────────────
    missing = [c for c in REQUIRED_CORE_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset missing required columns: {missing}. Found: {df.columns.tolist()}"
        )

    # Determine cost and rating column source names
    cost_source = RAW_COST_COL if RAW_COST_COL in df.columns else ("cost" if "cost" in df.columns else None)
    rating_source = RAW_RATING_COL if RAW_RATING_COL in df.columns else ("rating" if "rating" in df.columns else None)

    if not cost_source or not rating_source:
        missing_metric = []
        if not cost_source:
            missing_metric.append(RAW_COST_COL)
        if not rating_source:
            missing_metric.append(RAW_RATING_COL)
        raise ValueError(
            f"Dataset missing required metric columns: {missing_metric}. Found: {df.columns.tolist()}"
        )

    # Keep only target columns
    selected_cols = ["name", "location", "cuisines", cost_source, rating_source]
    df = df[selected_cols].copy()

    # ── Step 2: Rename columns ────────────────────────────────────────────────
    rename_mapping = {}
    if cost_source != "cost":
        rename_mapping[cost_source] = "cost"
    if rating_source != "rating":
        rename_mapping[rating_source] = "rating"

    if rename_mapping:
        df = df.rename(columns=rename_mapping)

    # ── Step 3: Type casting ──────────────────────────────────────────────────
    # Clean cost: extract digits, strip commas, handle 'N/A' or ranges
    extracted_cost = (
        df["cost"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")[0]
    )
    df["cost"] = (
        pd.to_numeric(extracted_cost, errors="coerce")
        .fillna(0)
        .astype(int)
    )
    # Ensure cost is non-negative
    df["cost"] = df["cost"].clip(lower=0)

    # Clean rating: e.g. '4.2/5', 'NEW', '-', None -> float 0.0 to 5.0
    split_rating = (
        df["rating"]
        .astype(str)
        .str.split("/")
        .str[0]
        .str.strip()
    )
    df["rating"] = (
        pd.to_numeric(split_rating, errors="coerce")
        .fillna(0.0)
        .astype(float)
    )
    # Clamp rating to [0.0, 5.0]
    df["rating"] = df["rating"].clip(lower=0.0, upper=5.0)

    # ── Step 4: Null handling ─────────────────────────────────────────────────
    # Drop rows missing name or location (None, NaN, or whitespace-only)
    df = df.dropna(subset=["name", "location"])
    df["name"] = df["name"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()
    df = df[(df["name"] != "") & (df["location"] != "")]

    # Fill optional/secondary fields
    df["cuisines"] = df["cuisines"].fillna("").astype(str)

    # ── Step 5: Cost normalization (Budget mapping) ───────────────────────────
    df["budget"] = df["cost"].apply(map_budget)

    # ── Step 6: Text normalization ────────────────────────────────────────────
    df["location"] = df["location"].str.lower().str.strip()
    df["cuisines"] = df["cuisines"].str.lower().str.strip()

    # ── Step 7: Deduplication ─────────────────────────────────────────────────
    # Sort by rating descending so the best-rated record is retained
    df = df.sort_values(by="rating", ascending=False)
    df = df.drop_duplicates(subset=["name", "location"], keep="first")
    df = df.reset_index(drop=True)

    # Reorder columns to standard schema
    canonical_order = ["name", "location", "cuisines", "cost", "budget", "rating"]
    df = df[canonical_order]

    # Verify post-condition: non-empty DataFrame
    if df.empty:
        logger.critical("DataFrame is empty after preprocessing.")
        raise RuntimeError("DataFrame is empty after preprocessing. Check the dataset.")

    logger.info(f"Preprocessing complete. {len(df):,} clean records ready.")
    return df
