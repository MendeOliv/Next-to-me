# mt5_connector.py
import os
from utils import logger


class MT5Connector:
    """Connector wrapper for MetaTrader5.

    Behavior:
    - In tests and when LIVE_MODE is False, acts as a safe stub.
    - In live mode, will attempt to import `MetaTrader5` and require credentials.
    """

    def __init__(self, login=None, password=None, server=None, max_retries=3):
        self.login = login or os.environ.get("MT5_LOGIN")
        self.password = password or os.environ.get("MT5_PASS")
        self.server = server or os.environ.get("MT5_SERVER")
        self.max_retries = max_retries
        self.connected = False
        self._mt5 = None

    def connect(self, live_mode=False):
        if not live_mode:
            logger.info("MT5Connector: running in stub mode (not live). Marking connected=True")
            self.connected = True
            return True

        # Live mode: require credentials
        if not (self.login and self.password):
            logger.error("MT5 credentials missing. Cannot connect in live mode.")
            return False

        try:
            import MetaTrader5 as mt5  # type: ignore

            self._mt5 = mt5
            # initialize connection
            try:
                success = mt5.initialize(login=int(self.login), password=self.password, server=self.server)
            except Exception:
                # older mt5 versions or local setup might require different args
                success = mt5.initialize()

            if not success:
                logger.error(f"MT5Connector: mt5.initialize() returned False: {mt5.last_error()}")
                return False

            # verify connection by checking account info
            info = mt5.account_info()
            if info is None:
                logger.error("MT5Connector: account_info() returned None after initialize")
                return False

            logger.info(f"MT5Connector: connected to MT5 account {info.login} on server {self.server}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"MT5Connector: failed to import/use MetaTrader5: {e}")
            return False

    def place_order(self, instrument, side, volume, price=None, sl=None, tp=None, live_mode=False):
        if not self.connected:
            ok = self.connect(live_mode=live_mode)
            if not ok:
                raise RuntimeError("MT5Connector: cannot place order because connection failed")

        # If running as stub, return simulated fill
        if not live_mode:
            return {
                "order_id": "mt5-sim-1",
                "instrument": instrument,
                "side": side,
                "volume": volume,
                "entry_price": price or 1.0,
                "status": "filled",
            }

        # Live mode: place an order using MetaTrader5
        if live_mode:
            # respect DRY_RUN env to avoid accidental live orders
            if os.environ.get("DRY_RUN", "False").lower() in ("1", "true", "yes", "y"):
                logger.info("DRY_RUN is enabled; skipping real order placement and returning simulated response.")
                return {
                    "order_id": "dryrun-1",
                    "instrument": instrument,
                    "side": side,
                    "volume": volume,
                    "entry_price": price or 1.0,
                    "status": "dryrun",
                }
            if not self._mt5:
                raise RuntimeError("MT5Connector: MetaTrader5 module not initialized")

            symbol = instrument
            # ensure symbol is selected/visible
            try:
                if not self._mt5.symbol_select(symbol, True):
                    logger.error(f"MT5Connector: failed to select symbol {symbol}")
                    raise RuntimeError(f"symbol_select failed for {symbol}")
            except Exception as e:
                logger.error(f"MT5Connector: symbol_select error for {symbol}: {e}")
                raise
            # build a market order request
            order_type = self._mt5.ORDER_TYPE_BUY if side.lower() == "buy" else self._mt5.ORDER_TYPE_SELL
            tick = self._mt5.symbol_info_tick(symbol)
            if tick is None:
                raise RuntimeError(f"MT5Connector: symbol_info_tick returned None for {symbol}")
            price = price or (tick.ask if side.lower() == "buy" else tick.bid)

            request = {
                "action": self._mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "price": float(price),
                "deviation": 10,
                "magic": 234000,
                "comment": "Next-to-me live order",
            }
            if sl is not None:
                request["sl"] = float(sl)
            if tp is not None:
                request["tp"] = float(tp)

            result = self._mt5.order_send(request)
            if result is None:
                raise RuntimeError("MT5Connector: order_send returned None")
            if result.retcode != self._mt5.TRADE_RETCODE_DONE:
                raise RuntimeError(f"MT5 order failed: {result.comment} retcode={result.retcode}")

            return {
                "order_id": getattr(result, "order", None),
                "instrument": instrument,
                "side": side,
                "volume": volume,
                "entry_price": float(result.price) if hasattr(result, "price") else price,
                "status": "filled",
            }

        # fallback (shouldn't reach here)
        return {
            "order_id": "mt5-sim-1",
            "instrument": instrument,
            "side": side,
            "volume": volume,
            "entry_price": price or 1.0,
            "status": "filled",
        }
