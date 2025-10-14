# tests/test_strategy.py
import pandas as pd
from strategy import generate_signals

def test_generate_signals():
    """
    Tests that the generate_signals function returns a DataFrame with a 'signal' column.
    """
    data = {'close': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]}
    df = pd.DataFrame(data)
    params = {'short_window': 2, 'long_window': 5}
    signals = generate_signals(df, params)
    assert isinstance(signals, pd.DataFrame)
    assert 'signal' in signals.columns
