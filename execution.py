# execution.py
import time, random
from utils import logger

class BaseExecution:
    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None):
        raise NotImplementedError

class SimulatedExecution(BaseExecution):
    def __init__(self, slippage_pips=1.0, spread_pips=0.1, pip_value=0.0001, latency_ms=100):
        self.slippage_pips = slippage_pips
        self.spread_pips = spread_pips
        self.pip_value = pip_value
        self.latency_ms = latency_ms

    def _simulate_fill_price(self, price, side):
        adj = (self.slippage_pips + self.spread_pips) * self.pip_value
        if side.lower() == "buy":
            return price + adj
        else:
            return price - adj

    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None):
        time.sleep(self.latency_ms / 1000.0)
        fill_price = self._simulate_fill_price(price, side)
        logger.debug(f"Simulated order fill: {instrument} {side} {volume} @ {fill_price}")
        return {
            "order_id": f"sim-{random.randint(100000,999999)}",
            "instrument": instrument,
            "side": side,
            "volume": volume,
            "entry_price": fill_price,
            "sl": sl,
            "tp": tp,
            "status": "filled"
        }

class LiveExecution(BaseExecution):
    def __init__(self, connector):
        self.conn = connector

    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None):
        return self.conn.place_order(instrument, side, volume, price=price, sl=sl, tp=tp)
