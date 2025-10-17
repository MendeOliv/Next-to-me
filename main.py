# main.py (substitui o ficheiro)
import os
import json
import time
import argparse
import asyncio
from dotenv import load_dotenv
from utils import logger, save_trades_csv
from core.engine import async_get_data, async_execute_trade
from signals.strategy import generate_signal

load_dotenv()

async def run_backtest(config_path=None):
    config_path = config_path or os.getenv('CONFIG_PATH', 'config.example.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    symbol = os.getenv('SYMBOL', 'EURUSD')
    timeframe = os.getenv('TIMEFRAME', '15m')

    logger.info(f"Starting backtest for {symbol} {timeframe}")
    data = await async_get_data(symbol=symbol, timeframe=timeframe, live=False)
    if data is None or getattr(data, "empty", True):
        logger.error("No data for backtest. Exiting.")
        return

    results = []
    balance = float(os.getenv('INITIAL_BALANCE', config.get('initial_balance', 10000)))
    risk_percent = float(os.getenv('RISK_PERCENT', config.get('risk', {}).get('risk_per_trade_pct', 0.02)))

    start_ts = time.time()
    for i in range(1, len(data)):
        df_slice = data.iloc[:i]
        signal = generate_signal(df_slice)  # synchronous small CPU op
        if signal:
            # use async_execute_trade wrapper to avoid blocking event loop
            result = await async_execute_trade(
                signal, balance, config, config.get('strategy', {}), df_slice['close'].iloc[-1], live=False
            )
            results.append(result)
            balance = result.get('balance_after', balance)
            logger.info(f"Trade executed. New balance: {balance:.2f}")

    elapsed = time.time() - start_ts
    save_trades_csv(results)
    logger.info(f"Backtest finished. Duration: {elapsed:.2f}s. Trades: {len(results)}")
    return results

async def run_live(poll_interval=60):
    logger.info("Live mode starting (async skeleton).")
    # Note: implement real streaming or polling here
    while True:
        # placeholder: sleep asynchronously
        await asyncio.sleep(poll_interval)

def main():
    parser = argparse.ArgumentParser(description="Next-to-me bot runner")
    parser.add_argument("--mode", choices=["backtest", "live"], default="backtest", help="run mode")
    parser.add_argument("--config", default=None, help="path to config json")
    args = parser.parse_args()

    if args.mode == "backtest":
        asyncio.run(run_backtest(config_path=args.config))
    else:
        # run live indefinitely
        try:
            asyncio.run(run_live())
        except KeyboardInterrupt:
            logger.info("Live run interrupted by user.")

if __name__ == "__main__":
    main()
