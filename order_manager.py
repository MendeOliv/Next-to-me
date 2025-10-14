# order_manager.py
from utils import get_logger, pips_to_price
from typing import Dict, Optional

logger = get_logger("order_manager")

class OrderManager:
    def __init__(self, atr_multiplier: float = 2.0):
        self.pending_orders: Dict = {}
        self.open_positions: Dict = {}
        self.atr_multiplier = atr_multiplier

    def add_pending_order(self, order_id, symbol, side, lots, entry_price, sl, tp):
        self.pending_orders[order_id] = {
            "symbol": symbol,
            "side": side,
            "lots": lots,
            "entry_price": entry_price,
            "sl": sl,
            "tp": tp,
        }
        logger.info(f"Added pending order: {order_id}")

    def reconcile_partial_fill(self, order_id, filled_lots):
        if order_id in self.pending_orders:
            self.pending_orders[order_id]['lots'] -= filled_lots
            if self.pending_orders[order_id]['lots'] <= 0:
                del self.pending_orders[order_id]
                logger.info(f"Pending order {order_id} fully filled.")
            else:
                logger.info(f"Pending order {order_id} partially filled. Remaining lots: {self.pending_orders[order_id]['lots']}")

    def update_trailing_stop(self, position_id, current_price, atr_pips):
        if position_id in self.open_positions:
            position = self.open_positions[position_id]
            new_sl = 0

            if position['side'] == 'buy':
                new_sl = current_price - pips_to_price(atr_pips * self.atr_multiplier)
                if new_sl > position['sl']:
                    position['sl'] = new_sl
                    logger.info(f"Updated trailing stop for position {position_id} to {new_sl}.")
            else: # Sell
                new_sl = current_price + pips_to_price(atr_pips * self.atr_multiplier)
                if new_sl < position['sl']:
                    position['sl'] = new_sl
                    logger.info(f"Updated trailing stop for position {position_id} to {new_sl}.")
