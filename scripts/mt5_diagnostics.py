import os
import MetaTrader5 as mt5  # type: ignore
from mt5_connector import MT5Connector


def pretty_error():
    try:
        err = mt5.last_error()
        print("mt5.last_error() ->", err)
    except Exception as e:
        print("could not get mt5.last_error():", e)


def run():
    print("mt5.version() ->", getattr(mt5, 'version', lambda: 'unknown')())
    try:
        ti = mt5.terminal_info()
        print("terminal_info() ->", ti)
    except Exception as e:
        print("terminal_info() failed:", e)

    print("Trying mt5.initialize() without credentials (connect to running terminal)")
    try:
        ok = mt5.initialize()
        print("initialize() ->", ok)
        pretty_error()
        if ok:
            try:
                acc = mt5.account_info()
                print("account_info() ->", acc)
            except Exception as e:
                print("account_info() failed:", e)
            mt5.shutdown()
    except Exception as e:
        print("initialize() without creds exception:", e)
        pretty_error()

    # try with credentials from env
    login = os.environ.get('MT5_LOGIN')
    password = os.environ.get('MT5_PASS')
    server = os.environ.get('MT5_SERVER')
    if login and password:
        print("Trying mt5.initialize() with credentials from env")
        try:
            ok = mt5.initialize(login=int(login), password=password, server=server)
            print("initialize(login) ->", ok)
            pretty_error()
            if ok:
                print("account_info() ->", mt5.account_info())
                mt5.shutdown()
        except Exception as e:
            print("initialize(login) exception:", e)
            pretty_error()
    else:
        print("No MT5_LOGIN/MT5_PASS in env to try credentialed initialize.")


if __name__ == '__main__':
    run()
