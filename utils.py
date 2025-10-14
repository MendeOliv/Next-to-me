# utils.py
import pandas as pd
import numpy as np

def price_to_pips(price_diff: float) -> float:
    # 1 pip in EURUSD = 0.0001
    return price_diff / 0.0001

def pips_to_price(pips: float) -> float:
    return pips * 0.0001

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    df must have columns: high, low, close
    returns a pandas Series of ATR values (same index as df)
    """
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr
