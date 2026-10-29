"""
tests/test_preprocessor.py
───────────────────────────
Unit tests for data/preprocessor.py.
Validates schema, null handling, type casting, normalization,
deduplication, budget tier mapping, and defensive edge cases.
"""

import pytest
import pandas as pd
from data.preprocessor import preprocess, map_budget


@pytest.fixture
def raw_df():
    """Synthetic raw dataset mimicking HuggingFace structure with edge cases."""
    return pd.DataFrame({
        "name": [
            "Spice Garden",
            "Pizza Hub",
            "Spice Garden",   # Duplicate with lower rating
            None,             # Missing name
            "Cafe Blend",
            "  ",             # Whitespace-only name
            "Burger Spot",
        ],
        "location": [
            "Delhi",
            "Bangalore",
            "Delhi",
            "Mumbai",
            "  Chennai  ",
            "Delhi",
            None,             # Missing location
        ],
        "cuisines": [
            "North Indian",
            "Italian",
            None,
            "Chinese",
            "Cafe, Bakery",
            "Fast Food",
            "American",
        ],
        "approx_cost(for two people)": [
            "800",
            "1,500",
            "800",
            "N/A",
            "300",
            "400",
            "600",
        ],
        "rate": [
            "4.2/5",
            "3.8/5",
            "3.5/5",          # Lower rating than the other Spice Garden
            "NEW",
            "4.7/5",
            "-",
            "4.0/5",
        ],
    })


def test_required_columns_present(raw_df):
    """Clean DataFrame must contain all canonical schema columns."""
    result = preprocess(raw_df)
    required = {"name", "location", "cuisines", "cost", "budget", "rating"}
    assert required.issubset(result.columns), f"Missing columns: {required - set(result.columns)}"


def test_null_names_dropped(raw_df):
    """Rows with null or whitespace-only names must be dropped."""
    result = preprocess(raw_df)
    assert result["name"].isna().sum() == 0
    assert (result["name"].str.strip() == "").sum() == 0
    assert None not in result["name"].values


def test_null_locations_dropped(raw_df):
    """Rows with null or whitespace-only locations must be dropped."""
    result = preprocess(raw_df)
    assert result["location"].isna().sum() == 0
    assert (result["location"].str.strip() == "").sum() == 0


def test_duplicates_removed(raw_df):
    """Deduplication on ['name', 'location'] must keep the highest rated row."""
    result = preprocess(raw_df)
    assert result.duplicated(subset=["name", "location"]).sum() == 0
    # For 'Spice Garden' in 'delhi', rating should be 4.2 (not 3.5)
    spice_garden = result[(result["name"] == "Spice Garden") & (result["location"] == "delhi")]
    assert len(spice_garden) == 1
    assert spice_garden.iloc[0]["rating"] == 4.2


def test_rating_within_range(raw_df):
    """All ratings must be floats in range [0.0, 5.0]."""
    result = preprocess(raw_df)
    assert result["rating"].between(0.0, 5.0).all()
    assert result["rating"].dtype in [float, "float64"]


def test_cost_non_negative(raw_df):
    """All cost values must be non-negative integers."""
    result = preprocess(raw_df)
    assert (result["cost"] >= 0).all()
    assert result["cost"].dtype in [int, "int64"]


def test_budget_valid_values(raw_df):
    """All budget values must belong to {'low', 'medium', 'high'}."""
    result = preprocess(raw_df)
    assert result["budget"].isin({"low", "medium", "high"}).all()


def test_location_normalized(raw_df):
    """Location strings must be lowercased and stripped of leading/trailing whitespace."""
    result = preprocess(raw_df)
    assert "chennai" in result["location"].values
    assert result["location"].eq(result["location"].str.lower().str.strip()).all()


def test_cuisines_normalized(raw_df):
    """Cuisines strings must be lowercased, stripped, and non-null."""
    result = preprocess(raw_df)
    assert result["cuisines"].isna().sum() == 0
    assert result["cuisines"].eq(result["cuisines"].str.lower().str.strip()).all()


def test_non_numeric_cost_handled():
    """Non-numeric cost values like 'N/A', comma-formatted, or ranges must be parsed safely."""
    df = pd.DataFrame({
        "name": ["A", "B", "C"],
        "location": ["loc1", "loc2", "loc3"],
        "cuisines": ["c1", "c2", "c3"],
        "approx_cost(for two people)": ["1,200", "N/A", "800-1000"],
        "rate": ["4.0/5", "4.0/5", "4.0/5"],
    })
    result = preprocess(df)
    assert result.loc[result["name"] == "A", "cost"].iloc[0] == 1200
    assert result.loc[result["name"] == "B", "cost"].iloc[0] == 0
    assert result.loc[result["name"] == "C", "cost"].iloc[0] == 800


def test_non_numeric_rating_handled():
    """Non-numeric ratings like 'NEW', '-', None must convert to 0.0 float without error."""
    df = pd.DataFrame({
        "name": ["A", "B", "C"],
        "location": ["loc1", "loc2", "loc3"],
        "cuisines": ["c1", "c2", "c3"],
        "approx_cost(for two people)": ["500", "500", "500"],
        "rate": ["NEW", "-", None],
    })
    result = preprocess(df)
    assert (result["rating"] == 0.0).all()


@pytest.mark.parametrize("cost,expected_budget", [
    (0,    "low"),
    (500,  "low"),
    (501,  "medium"),
    (1200, "medium"),
    (1201, "high"),
    (5000, "high"),
])
def test_budget_mapping(cost, expected_budget):
    """Test cost-to-budget tier mapping against expected thresholds."""
    assert map_budget(cost) == expected_budget


def test_missing_required_columns_raises_error():
    """Must raise ValueError when required columns are absent."""
    broken_df = pd.DataFrame({
        "name": ["Restaurant A"],
        # Missing 'location', 'cuisines', etc.
    })
    with pytest.raises(ValueError, match="Dataset missing required columns"):
        preprocess(broken_df)


def test_empty_dataframe_raises_runtime_error():
    """Must raise RuntimeError when input DataFrame is empty or produces 0 records."""
    empty_df = pd.DataFrame(columns=["name", "location", "cuisines", "approx_cost(for two people)", "rate"])
    with pytest.raises(RuntimeError):
        preprocess(empty_df)


def test_row_count_after_preprocessing(raw_df):
    """Clean DataFrame must retain valid records."""
    result = preprocess(raw_df)
    assert len(result) > 0
