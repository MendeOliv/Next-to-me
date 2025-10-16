# data_handler.py
import pandas as pd

def load_csv_data(path, parse_dates=True):
    df = pd.read_csv(path)
    if parse_dates:
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            df.set_index('timestamp', inplace=True)
    df = df[~df.index.duplicated(keep='first')].sort_index()
    df = df.ffill()
    return df

def resample_df(df, timeframe="15T"):
    ohlc = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    return df.resample(timeframe).apply(ohlc).dropna()
