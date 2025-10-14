# execution.py
import logging
from typing import Optional
from mt5_connector import send_market_order as mt5_send_market_order

class ExecutionHandler:
    """
    Handles order execution for both live and paper trading modes.
    """
    def __init__(self, paper_trading: bool = False):
        self.paper_trading = paper_trading

    def send_market_order(self, symbol: str, lot: float, side: str, sl: Optional[float] = None, tp: Optional[float] = None, comment: str = ''):
        """
        Sends a market order. In paper trading mode, it logs the order instead of executing it.
        """
        if self.paper_trading:
            logging.info(f"[PAPER] Send market order: {side} {lot} {symbol} SL={sl} TP={tp}")
            return None  # In paper mode, we don't have a real result

        try:
            result = mt5_send_market_order(symbol, lot, side, sl=sl, tp=tp, comment=comment)
            logging.info(f"Sent market order, result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error sending market order: {e}")
            return None
