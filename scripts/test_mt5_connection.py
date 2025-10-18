import os
import time
from mt5_connector import MT5Connector
from utils import logger


def main():
    login = os.environ.get("MT5_LOGIN")
    password = os.environ.get("MT5_PASS")
    server = os.environ.get("MT5_SERVER")
    symbol = os.environ.get("SYMBOL", "EURUSD")

    if not (login and password and server):
        print("MT5 credentials not found in environment. Set MT5_LOGIN, MT5_PASS and MT5_SERVER.")
        return

    print("Initializing MT5Connector in live mode (demo)")
    conn = MT5Connector(login=login, password=password, server=server)
    ok = conn.connect(live_mode=True)
    print("connect() ->", ok)
    if not ok:
        print("Failed to connect to MT5. Aborting.")
        return

    # show account info
    try:
        info = conn._mt5.account_info()
        print("Account info:", info)
    except Exception as e:
        print("Could not fetch account_info():", e)

    # small test order (demo). Volume small: 0.01
    try:
        print(f"Placing demo market BUY order for {symbol} volume=0.01")
        res = conn.place_order(instrument=symbol, side='buy', volume=0.01, live_mode=True)
        print("Order result:", res)
    except Exception as e:
        print("Order failed:", e)


if __name__ == '__main__':
    main()
