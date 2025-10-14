# order_manager.py
from utils import pips_to_price, price_to_pips
from mt5_connector import send_market_order
from typing import Optional

ATR_MULTIPLIER_15M = 1.8
ATR_MULTIPLIER_4H = 3.0

def calculate_trailing_stop(entry_price: float, highest_since_entry: float, atr_value_pips: float, side: str, timeframe: str) -> float:
    """
    Returns desired stop price (absolute) based on ATR multiplier and highest/lowest since entry.
    """
    if timeframe == '15m':
        mult = ATR_MULTIPLIER_15M
    else:
        mult = ATR_MULTIPLIER_4H
    trail_pips = atr_value_pips * mult
    trail_price_diff = pips_to_price(trail_pips)
    if side == 'buy':
        desired_stop = highest_since_entry - trail_price_diff
    else:
        desired_stop = highest_since_entry + trail_price_diff
    return desired_stop

def open_order(symbol: str, side: str, lots: float, entry_price: float, stop_pips: float, tp_pips: Optional[float] = None, comment: str = ''):
    """
    Convenience wrapper: calculates absolute SL/TP and sends market order.
    entry_price parameter used for calculating SL/TP price (it's approximate).
    """
    sl_price = None
    tp_price = None
    if side == 'buy':
        sl_price = entry_price - pips_to_price(stop_pips)
        if tp_pips:
            tp_price = entry_price + pips_to_price(tp_pips)
    else:
        sl_price = entry_price + pips_to_price(stop_pips)
        if tp_pips:
            tp_price = entry_price - pips_to_price(tp_pips)

    result = send_market_order(symbol, lots, side, sl=sl_price, tp=tp_price, comment=comment)
    return result
