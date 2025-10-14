# strategy.py
import pandas as pd
from utils import get_logger

logger = get_logger("strategy")

def generate_signals(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Generates trading signals based on the provided dataframe and parameters.
    Returns a DataFrame with a 'signal' column (1 for buy, -1 for sell, 0 for hold).
    """
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0

    # Example strategy: simple moving average crossover
    short_window = int(params.get('short_window', 50))
    long_window = int(params.get('long_window', 200))

    signals['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['signal'][short_window:] = \
        pd.np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1, 0)

    signals['positions'] = signals['signal'].diff()

    logger.info("Generated signals.")
    return signals
