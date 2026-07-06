from functools import lru_cache
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

SUMMARY_PATH = DATA_DIR / "business_daily_summary.csv"
CHANNEL_PATH = DATA_DIR / "channel_daily_performance.csv"


@lru_cache(maxsize=1)
def load_summary_data() -> pd.DataFrame:
    """Load the processed daily business summary dataset."""
    df = pd.read_csv(SUMMARY_PATH)
    df["DATE_DAY"] = pd.to_datetime(df["DATE_DAY"])
    return df


@lru_cache(maxsize=1)
def load_channel_data() -> pd.DataFrame:
    """Load the processed daily channel performance dataset."""
    df = pd.read_csv(CHANNEL_PATH)
    df["DATE_DAY"] = pd.to_datetime(df["DATE_DAY"])
    return df
