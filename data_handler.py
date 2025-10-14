# data_handler.py
import pandas as pd

def load_historical_data(filepath: str) -> pd.DataFrame:
    """
    Loads historical OHLC data from a CSV file.

    Args:
        filepath: The path to the CSV file.

    Returns:
        A pandas DataFrame with the loaded data.
    """
    try:
        df = pd.read_csv(filepath, parse_dates=['datetime'])
        return df
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return pd.DataFrame()
