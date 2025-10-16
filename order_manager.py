# order_manager.py
from utils import logger

class OrderManager:
    def __init__(self):
        self.open_orders = {}
        self.positions = {}

    def register_order(self, order):
        self.open_orders[order['order_id']] = order
        logger.debug(f"Registered order {order['order_id']}")

    def close_order(self, order_id, exit_price, pnl):
        order = self.open_orders.pop(order_id, None)
        if order:
            logger.info(f"Order {order_id} closed with PnL {pnl}")
            inst = order['instrument']
            self.positions.pop(inst, None)
        else:
            logger.warning(f"close_order called for unknown order {order_id}")
