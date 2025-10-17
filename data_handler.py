# data_handler.py
import pandas as pd

def load_csv_data(path, parse_dates=True):
    df = pd.read_csv(path)
    if parse_dates:
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            df.set_index('timestamp', inplace=True)
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
            df.set_index('datetime', inplace=True)
    # drop duplicates and sort
    df = df[~df.index.duplicated(keep='first')].sort_index()
    # forward fill missing
    df = df.ffill()
    return df
