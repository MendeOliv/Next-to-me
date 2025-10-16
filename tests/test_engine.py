# tests/test_engine.py
from core.engine import execute_trade

def test_execute_trade_simulate():
    result = execute_trade('buy', 10000, 0.02, live=False)
    assert 'pnl' in result
    assert result['balance_after'] > 10000
