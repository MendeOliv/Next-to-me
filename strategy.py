# strategy.py
import pandas as pd
import numpy as np

def generate_sma_signals(df, short_window=20, long_window=50):
    """
    Returns DataFrame with columns: short_mavg, long_mavg, signal (1 buy, 0 flat), signal_change
    df must have 'close' column and DatetimeIndex
    """
    df = df.copy()
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    df['signal'] = 0
    idx_start = long_window
    cond = df['short_mavg'] > df['long_mavg']
    df.loc[cond.index[idx_start:], 'signal'] = np.where(cond[idx_start:], 1, 0)
    df['signal_change'] = df['signal'].diff().fillna(0)
    return df
