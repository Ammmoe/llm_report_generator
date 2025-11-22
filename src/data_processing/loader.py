import pandas as pd
from src.config import DATASET_PATH


def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load BMW sales dataset."""
    df = pd.read_csv(path)
    return df


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preprocessing – you will expand later.
    """
    df = df.copy()
    # Example: ensure correct types
    if "year" in df.columns:
        df["year"] = df["year"].astype(int)
    return df
