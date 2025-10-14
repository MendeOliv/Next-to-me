# tests/test_utils.py
from utils import price_to_pips, pips_to_price

def test_price_to_pips():
    """
    Tests that the price is converted to pips correctly.
    """
    pips = price_to_pips(0.0001)
    assert pips == 1

def test_pips_to_price():
    """
    Tests that pips are converted to price correctly.
    """
    price = pips_to_price(1)
    assert price == 0.0001
