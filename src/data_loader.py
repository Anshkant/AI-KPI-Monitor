import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_path(rel_path: str) -> str:
    """Finds the dataset file, automatically checking for .gz compressed or uncompressed variants."""
    full_path = os.path.join(BASE_DIR, rel_path) if not os.path.isabs(rel_path) else rel_path

    if os.path.exists(full_path):
        return full_path

    if os.path.exists(full_path + ".gz"):
        return full_path + ".gz"

    if full_path.endswith(".gz") and os.path.exists(full_path[:-3]):
        return full_path[:-3]

    return full_path


def load_dataset(rel_path: str = "data/processed/clean_sales_data.csv") -> pd.DataFrame:
    """Loads a CSV or GZ-compressed CSV dataset seamlessly."""
    path = get_data_path(rel_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {rel_path} (checked {path})")
    return pd.read_csv(path)
