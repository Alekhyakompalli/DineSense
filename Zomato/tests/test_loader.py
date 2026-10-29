"""
tests/test_loader.py
────────────────────
Unit tests for data/loader.py.
Tests successful dataset loading and defensive error handling on network failure.
"""

from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from datasets import Dataset, DatasetDict
from data.loader import load_zomato_dataset


def test_load_zomato_dataset_success():
    """Verify that load_zomato_dataset converts HuggingFace dataset to a pandas DataFrame."""
    mock_hf_dataset = Dataset.from_dict({
        "name": ["Test Bistro"],
        "location": ["Test City"],
        "cuisines": ["Cafe"],
        "approx_cost(for two people)": ["500"],
        "rate": ["4.5/5"],
    })
    mock_dict = DatasetDict({"train": mock_hf_dataset})

    with patch("data.loader.load_dataset", return_value=mock_dict):
        df = load_zomato_dataset("mock-repo/dataset")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["name"] == "Test Bistro"


def test_load_zomato_dataset_failure_raises_runtime_error():
    """Verify that a network or repo error raises a RuntimeError with descriptive message."""
    with patch("data.loader.load_dataset", side_effect=ConnectionError("HF Hub Unreachable")):
        with pytest.raises(RuntimeError, match="Could not load the Zomato dataset"):
            load_zomato_dataset("mock-repo/dataset")
