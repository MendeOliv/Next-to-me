# execution.py
from typing import Optional
from mt5_connector import send_market_order as mt5_send_market_order
from utils import get_logger
import random
import pandas as pd

logger = get_logger("execution")

def simulate_order_fill(price, side, volume, slippage_pips=1.0, spread_pips=0.1, pip_value=0.0001):
    # slippage_pips: average adverse slippage in pips
    adj = (slippage_pips + spread_pips) * pip_value
    if side.lower() == "buy":
        fill_price = price + adj
    else:
        fill_price = price - adj
    logger.debug(f"Simulated fill: side={side}, price={price} -> fill_price={fill_price}")
    return fill_price

def log_trade(trade_data, log_file="trades.csv"):
    df = pd.DataFrame([trade_data])
    df.to_csv(log_file, mode='a', header=not pd.io.common.file_exists(log_file), index=False)
    logger.info(f"Trade logged: {trade_data}")

def simulate_adverse_scenario(slippage_pips, reject_probability):
    """
    Simulates adverse scenarios by increasing slippage or rejecting orders.
    """
    if random.random() < reject_probability:
        logger.warning("Simulating order rejection.")
        return None

    # Increase slippage in high volatility
    increased_slippage = slippage_pips * random.uniform(2, 5)
    logger.warning(f"Simulating high volatility with slippage: {increased_slippage} pips")
    return increased_slippage

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
            logger.info(f"[PAPER] Send market order: {side} {lot} {symbol} SL={sl} TP={tp}")
            return None  # In paper mode, we don't have a real result

        try:
            result = mt5_send_market_order(symbol, lot, side, sl=sl, tp=tp, comment=comment)
            logger.info(f"Sent market order, result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error sending market order: {e}")
            return None
