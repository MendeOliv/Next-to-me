# tests/test_risk_management.py
from risk_management import position_size
import pytest

def test_position_size():
    """
    Tests that the lot size is computed correctly.
    """
    balance = 100000
    risk_per_trade_pct = 1.0
    stop_loss_pips = 100
    pip_value = 10.0
    lot_size = position_size(balance, risk_per_trade_pct, stop_loss_pips, pip_value)
    assert lot_size == 0.1

def test_position_size_with_zero_stop_loss():
    """
    Tests that the function raises a ValueError if the stop loss is 0.
    """
    balance = 100000
    risk_per_trade_pct = 1.0
    stop_loss_pips = 0
    pip_value = 10.0
    with pytest.raises(ValueError):
        position_size(balance, risk_per_trade_pct, stop_loss_pips, pip_value)
