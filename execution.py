# execution.py
import time, random
from utils import logger

class SimulatedExecution:
    def __init__(self, slippage_pips=1.0, spread_pips=0.1, pip_size=0.0001, latency_ms=0):
        self.slippage_pips = slippage_pips
        self.spread_pips = spread_pips
        self.pip_size = pip_size  # incremento de preço por pip
        self.latency_ms = latency_ms

    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None):
        # simulate latency
        if self.latency_ms:
            time.sleep(self.latency_ms/1000.0)
        adj = (self.slippage_pips + self.spread_pips) * self.pip_size
        if side.lower() == 'buy':
            fill_price = price + adj
        else:
            fill_price = price - adj
        order_id = f"sim-{random.randint(1000,9999)}"
        logger.debug(f"Simulated fill {order_id} {instrument} {side} {volume} @ {fill_price}")
        return {'order_id': order_id, 'instrument': instrument, 'side': side, 'volume': volume, 'entry_price': fill_price, 'status':'filled'}
