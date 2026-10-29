"""
data/loader.py
──────────────
Loads the Zomato restaurant dataset from HuggingFace Hub.
Handles network errors, logging, and conversion to a pandas DataFrame.
"""

import pandas as pd
from datasets import load_dataset
from config.settings import DATASET_NAME
from utils.logger import get_logger

logger = get_logger(__name__)


def load_zomato_dataset(dataset_name: str = DATASET_NAME) -> pd.DataFrame:
    """
    Load the Zomato dataset from HuggingFace Hub and return as a raw DataFrame.

    Args:
        dataset_name: HuggingFace repository identifier (defaults to config setting).

    Returns:
        pd.DataFrame: Raw dataset as a pandas DataFrame.

    Raises:
        RuntimeError: If the dataset cannot be fetched or converted.
    """
    logger.info(f"Loading Zomato dataset '{dataset_name}' from HuggingFace Hub...")
    try:
        dataset = load_dataset(dataset_name)
        if "train" in dataset:
            df = dataset["train"].to_pandas()
        else:
            first_split = next(iter(dataset.keys()))
            df = dataset[first_split].to_pandas()

        logger.info(f"Successfully loaded {len(df):,} records from HuggingFace dataset.")
        return df
    except Exception as e:
        logger.critical(f"Failed to load dataset '{dataset_name}' from HuggingFace: {e}")
        raise RuntimeError(
            f"Could not load the Zomato dataset from HuggingFace ({dataset_name}). "
            "Please check your internet connection or verify the dataset repository."
        ) from e
