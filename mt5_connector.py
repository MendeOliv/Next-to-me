# mt5_connector.py
import MetaTrader5 as mt5
from typing import Optional
import time
import os
from utils import get_logger

logger = get_logger("mt5_connector")

def connect():
    login = os.environ.get("MT5_LOGIN")
    password = os.environ.get("MT5_PASSWORD")
    server = os.environ.get("MT5_SERVER")

    if not mt5.initialize():
        logger.error(f"MT5 initialize failed, last_error={mt5.last_error()}")
        raise RuntimeError(f"MT5 initialize failed, last_error={mt5.last_error()}")

    if not mt5.login(int(login), password, server):
        logger.error(f"MT5 login failed, last_error={mt5.last_error()}")
        raise RuntimeError(f"MT5 login failed, last_error={mt5.last_error()}")

    logger.info("Connecting to MT5 with login: %s", login)

def shutdown():
    mt5.shutdown()
    logger.info("MT5 connection shut down.")

def place_order(symbol: str, lot: float, side: str, sl: Optional[float] = None, tp: Optional[float] = None, comment: str = ''):
    request_type = mt5.ORDER_TYPE_BUY if side.lower() == 'buy' else mt5.ORDER_TYPE_SELL
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"Symbol tick not available for {symbol}.")
        raise RuntimeError("Symbol tick not available: " + symbol)
    price = tick.ask if side.lower() == 'buy' else tick.bid
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot),
        "type": request_type,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": comment,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    if sl is not None:
        request['sl'] = float(sl)
    if tp is not None:
        request['tp'] = float(tp)
    result = mt5.order_send(request)
    logger.info(f"Order send result: {result}")
    return result

def get_positions():
    positions = mt5.positions_get()
    if positions is None:
        return []
    return positions

def is_connected():
    """
    Checks if the terminal is connected to the trade server.
    """
    connected = mt5.terminal_info().connected
    logger.debug(f"MT5 connection status: {connected}")
    return connected
