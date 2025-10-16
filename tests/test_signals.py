# tests/test_signals.py
import pandas as pd
from signals.strategy import generate_signal

def test_generate_signal_buy():
    # RSI abaixo de 30 deve sinalizar compra
    close_prices = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 4, 3, 2, 1]
    df = pd.DataFrame({'close': close_prices})
    assert generate_signal(df) == 'buy'

def test_generate_signal_sell():
    # RSI acima de 70 deve sinalizar venda
    close_prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    df = pd.DataFrame({'close': close_prices})
    assert generate_signal(df) == 'sell'

def test_generate_signal_none():
    # RSI neutro não deve sinalizar nada
    close_prices = [100] * 15
    df = pd.DataFrame({'close': close_prices})
    assert generate_signal(df) is None
