# tests/test_integration.py
from execution import SimulatedExecution
from risk_management import position_size

def test_simulated_fill_and_size():
    execu = SimulatedExecution(slippage_pips=1.0, spread_pips=0.1, pip_value=10.0, latency_ms=0)
    res = execu.place_order("EURUSD", "buy", 0.1, price=1.1000)
    assert res['status'] == "filled"
    vol = position_size(10000, 1.0, 50, 10.0)
    assert vol > 0
