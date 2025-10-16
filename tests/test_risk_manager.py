# tests/test_risk_management.py
from risk_management import calculate_position_size

def test_calculate_position_size():
    assert calculate_position_size(10000, 50, 0.02) == 4.0

def test_calculate_position_size_zero_stop():
    assert calculate_position_size(10000, 0, 0.02) == 0
