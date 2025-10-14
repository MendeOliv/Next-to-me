# main.py
import argparse
import sys
import logging
import backtest_eurusd_ftmo as bt
from utils import setup_logging

def run_backtest(data_csv):
    bt.backtest(data_csv)

from execution import ExecutionHandler
import time

def run_live(paper_trading: bool = False):
    from mt5_connector import initialize, shutdown, account_info, is_connected

    while True:
        try:
            if not is_connected():
                logging.warning("MT5 connection lost. Attempting to reconnect...")
                initialize()

            info = account_info()
            logging.info(f"Account info: {info}")

            execution_handler = ExecutionHandler(paper_trading=paper_trading)

            if paper_trading:
                logging.info("Running in paper trading mode.")
                # Example of sending a paper trade
                execution_handler.send_market_order("EURUSD", 0.1, "buy", sl=1.1000, tp=1.1200)

            # Main trading logic would go here

            time.sleep(60) # Pause for 60 seconds before the next check

        except RuntimeError as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(60) # Wait before retrying
        except KeyboardInterrupt:
            logging.info("Shutting down the bot.")
            shutdown()
            break

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['dryrun', 'live', 'paper'], default='dryrun')
    parser.add_argument('--data', help='CSV 15m for dryrun/backtest')
    args = parser.parse_args()
    if args.mode == 'dryrun':
        if not args.data:
            logging.error("Please provide --data for dryrun (path to CSV 15m).")
            sys.exit(1)
        run_backtest(args.data)
    elif args.mode == 'paper':
        run_live(paper_trading=True)
    else:
        run_live()
