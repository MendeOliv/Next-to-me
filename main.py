import os
import json
import time
import argparse
import asyncio
from dotenv import load_dotenv
from utils import logger, save_trades_csv
from core.engine import async_get_data, async_execute_trade
from signals.strategy import generate_signal
from config_loader import load_config, get_bool_env

load_dotenv()


async def run_backtest(config):
    symbol = config.get("instrument") or os.getenv("SYMBOL", "EURUSD")
    timeframe = config.get("timeframe") or os.getenv("TIMEFRAME", "15m")

    logger.info(f"Starting backtest for {symbol} {timeframe}")
    data = await async_get_data(symbol=symbol, timeframe=timeframe, live=False)
    if data is None or getattr(data, "empty", True):
        logger.error("No data for backtest. Exiting.")
        return

    results = []
    balance = float(os.getenv("INITIAL_BALANCE", config.get("initial_balance", 10000)))

    start_ts = time.time()
    for i in range(1, len(data)):
        df_slice = data.iloc[:i]
        signal = generate_signal(df_slice)  # synchronous small CPU op
        if signal:
            result = await async_execute_trade(
                signal, balance, config, config.get("strategy", {}), df_slice["close"].iloc[-1], live=False
            )
            results.append(result)
            balance = result.get("balance_after", balance)
            logger.info(f"Trade executed. New balance: {balance:.2f}")

    elapsed = time.time() - start_ts
    save_trades_csv(results)
    logger.info(f"Backtest finished. Duration: {elapsed:.2f}s. Trades: {len(results)}")
    return results


async def run_live(config, poll_interval=60):
    logger.info("Live mode starting (safety checks in place).")
    # Safety: ensure LIVE_CONFIRM is explicitly set
    if not get_bool_env("LIVE_CONFIRM", False):
        logger.error("LIVE_CONFIRM not enabled. Set LIVE_CONFIRM=YES to allow live trading.")
        return

    # TODO: implementar loop de dados real com reconexões e backoff
    while True:
        await asyncio.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="Next-to-me bot runner")
    parser.add_argument("--mode", choices=["backtest", "live"], default="backtest", help="run mode")
    parser.add_argument("--config", default=None, help="path to config json")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.mode == "backtest":
        asyncio.run(run_backtest(config))
    else:
        try:
            asyncio.run(run_live(config))
        except KeyboardInterrupt:
            logger.info("Live run interrupted by user.")


if __name__ == "__main__":
    main()
