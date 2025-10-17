# tests/test_engine.py
from core.engine import execute_trade

def test_execute_trade_simulate():
    config = {
        "instrument": "EURUSD",
        "risk": {"risk_per_trade_pct": 0.02},
        "execution": {"slippage_pips": 1.0, "spread_pips": 0.1, "pip_value": 10.0}
    }
    strategy_config = {"stop_loss_pips": 50, "take_profit_pips": 100}

    result = execute_trade('buy', 10000, config, strategy_config, 1.1000, live=False)
    assert 'pnl' in result
    assert result['balance_after'] > 10000
