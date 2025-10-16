# signals/strategy.py
import pandas as pd
# import talib as ta  # Assuma importado; se não, use pandas rolling

def generate_signal(df):
    if len(df) < 14:
        return None  # Evite cálculos em dados incompletos
    # df['rsi'] = ta.RSI(df['close'], timeperiod=14)
    # Placeholder for RSI calculation using pandas rolling
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    if df['rsi'].iloc[-1] > 70:
        return 'sell'
    elif df['rsi'].iloc[-1] < 30:
        return 'buy'
    return None
