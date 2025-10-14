# mt5_connector.py
import MetaTrader5 as mt5
from typing import Optional
import time
import os
from dotenv import load_dotenv

load_dotenv()

def initialize(path: Optional[str] = None) -> bool:
    """
    Initializes MT5. Optionally, you can provide the path to the terminal.
    Example: initialize(r"C:\\Program Files\\MetaTrader 5\\terminal64.exe")
    """
    if path:
        res = mt5.initialize(path)
    else:
        res = mt5.initialize()

    if not res:
        raise RuntimeError(f"MT5 initialize failed, last_error={mt5.last_error()}")

    # Login with credentials from .env file
    login = int(os.getenv("MT5_LOGIN", "0"))
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "")

    if not mt5.login(login, password, server):
        raise RuntimeError(f"MT5 login failed, last_error={mt5.last_error()}")

    return True

def shutdown():
    mt5.shutdown()

def account_info():
    info = mt5.account_info()
    return info._asdict() if info else None

def get_rates(symbol: str, timeframe, n=500):
    """
    Wrapper to mt5.copy_rates_from_pos
    timeframe: mt5.TIMEFRAME_M1, TIMEFRAME_M5, TIMEFRAME_M15, TIMEFRAME_H4, etc.
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None:
        return None
    import pandas as pd
    df = pd.DataFrame(rates)
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df = df[['datetime', 'open', 'high', 'low', 'close', 'tick_volume']].rename(columns={'tick_volume':'volume'})
    return df

def send_market_order(symbol: str, lot: float, side: str, sl: Optional[float] = None, tp: Optional[float] = None, comment: str = ''):
    """
    Envia ordem de mercado (market order). sl/tp são preços absolutos.
    side: 'buy' ou 'sell'
    """
    request_type = mt5.ORDER_TYPE_BUY if side.lower() == 'buy' else mt5.ORDER_TYPE_SELL
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
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
    return result

def close_position_by_ticket(ticket: int):
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        return None
    pos = pos[0]
    symbol = pos.symbol
    volume = pos.volume
    side = 'sell' if pos.type == mt5.ORDER_TYPE_BUY else 'buy'
    return send_market_order(symbol, volume, side, comment=f"close-{ticket}")

def is_connected():
    """
    Checks if the terminal is connected to the trade server.
    """
    return mt5.terminal_info().connected
