# data_handler.py
import pandas as pd
from utils import get_logger

logger = get_logger("data_handler")

def load_csv_data(path) -> pd.DataFrame:
    """
    Loads historical data from a CSV file, normalizes timestamps to UTC,
    and validates the data.
    """
    df = pd.read_csv(path, parse_dates=True, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)

    # Validate data
    if df.isnull().values.any():
        logger.warning("NaN values found in data. Applying forward-fill.")
        df.fillna(method='ffill', inplace=True)
    if df.index.duplicated().any():
        logger.warning("Duplicate timestamps found. Removing duplicates.")
        df = df[~df.index.duplicated(keep='first')]

    logger.info(f"Loaded and validated data from {path}.")
    return df

def resample(df, timeframe) -> pd.DataFrame:
    """
    Resamples the dataframe to the given timeframe.
    """
    return df.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
