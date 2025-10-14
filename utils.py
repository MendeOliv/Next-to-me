# utils.py
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import os

def get_logger(name="next_to_me", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(os.path.join(log_dir, f"{name}.log"), maxBytes=5_000_000, backupCount=5)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

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
