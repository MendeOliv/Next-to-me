# mt5_connector.py
import time
import random
from utils import logger
import os

try:
    import MetaTrader5 as mt5
except Exception:
    mt5 = None
    logger.warning("MetaTrader5 package not available; live execution disabled")

class MT5Connector:
    def __init__(self, login=None, password=None, server=None, max_retries=5):
        self.login = login or os.environ.get("MT5_LOGIN")
        self.password = password or os.environ.get("MT5_PASS")
        self.server = server or os.environ.get("MT5_SERVER")
        self.max_retries = max_retries
        self.connected = False

    def connect(self):
        attempt = 0
        while attempt < self.max_retries:
            try:
                if mt5 is None:
                    raise RuntimeError("MT5 library not installed")
                ok = mt5.initialize(login=int(self.login), password=self.password, server=self.server)
                if ok:
                    self.connected = True
                    logger.info("MT5 connected")
                    return True
                else:
                    raise RuntimeError("MT5 initialize returned False")
            except Exception as e:
                attempt += 1
                wait = 2 ** attempt
                logger.warning(f"MT5 connect attempt {attempt} failed: {e}. Retry in {wait}s")
                time.sleep(wait)
        logger.error("MT5 connect failed after retries")
        raise ConnectionError("MT5 connect failed")

    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None):
        if not self.connected:
            self.connect()
        attempt = 0
        while attempt < self.max_retries:
            try:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": instrument,
                    "volume": float(volume),
                    "type": mt5.ORDER_TYPE_BUY if side.lower() == "buy" else mt5.ORDER_TYPE_SELL,
                    "price": price,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": "next_to_me"
                }
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"MT5 order placed: {result.order}")
                    return {
                        "order_id": result.order,
                        "instrument": instrument,
                        "side": side,
                        "volume": volume,
                        "entry_price": result.price,
                        "status": "filled"
                    }
                else:
                    raise RuntimeError(f"MT5 order failed: {getattr(result,'comment',result)}")
            except Exception as e:
                attempt += 1
                wait = 2 ** attempt
                logger.warning(f"MT5 place_order attempt {attempt} failed: {e}. Retry in {wait}s")
                time.sleep(wait)
        logger.error("MT5 place_order failed after retries")
        raise RuntimeError("MT5 place_order failed")
