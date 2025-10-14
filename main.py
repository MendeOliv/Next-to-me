# main.py
import argparse
import sys
import time
import json
import subprocess
import backtest_eurusd_ftmo as bt
from utils import get_logger
from execution import ExecutionHandler
from risk_management import load_risk_state, save_risk_state, position_size
from strategy import generate_signals
from data_handler import resample

logger = get_logger("main")

def watchdog_check(state, config):
    # state: { "balance":..., "max_drawdown":..., "daily_loss":... }
    if state["daily_loss_pct"] >= config["risk"]["max_daily_loss_pct"]:
        logger.error("Max daily loss exceeded. Shutting down.")
        return False
    if state["total_drawdown_pct"] >= config["risk"]["max_total_loss_pct"]:
        logger.critical("Max total loss exceeded. Shutting down permanently.")
        return False
    return True

def run_backtest(data_csv):
    config = json.load(open("config.json"))
    bt.backtest(data_csv, config)

def run_live(paper_trading: bool = False):
    from mt5_connector import connect, shutdown, get_positions, place_order, get_rates, is_connected

    config = json.load(open("config.json"))
    risk_state = load_risk_state()
    initial_balance = risk_state.get("balance", config["initial_balance"])

    while True:
        try:
            if not is_connected():
                logger.warning("MT5 connection lost. Attempting to reconnect...")
                connect()

            if not watchdog_check(risk_state, config):
                shutdown()
                break

            # Fetch live data
            rates_df = get_rates(config['instrument'], config['timeframe'])

            # Generate signals
            params = config.get('strategy_params', {'short_window': 50, 'long_window': 200})
            signals = generate_signals(rates_df, params)

            # Execute trades
            if signals['positions'].iloc[-1] == 1.0: # Buy signal
                stop_loss_pips = 100 # Example stop loss
                lot_size = position_size(risk_state['balance'], config['risk']['risk_per_trade_pct'], stop_loss_pips, config['execution']['pip_value'])
                place_order(config['instrument'], lot_size, 'buy', sl=rates_df['close'].iloc[-1] - stop_loss_pips * config['execution']['pip_value'])

            save_risk_state(risk_state)
            time.sleep(60)

        except RuntimeError as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down the bot.")
            shutdown()
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['dryrun', 'live', 'paper'], default='dryrun')
    parser.add_argument('--data', help='CSV 15m for dryrun/backtest')
    args = parser.parse_args()

    # Save a snapshot of the config and git commit hash
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    config = json.load(open("config.json"))
    config['git_hash'] = git_hash
    with open(f"config_snapshot_{int(time.time())}.json", 'w') as f:
        json.dump(config, f, indent=4)

    if args.mode == 'dryrun':
        if not args.data:
            logger.error("Please provide --data for dryrun (path to CSV 15m).")
            sys.exit(1)
        run_backtest(args.data)
    elif args.mode == 'paper':
        run_live(paper_trading=True)
    else:
        run_live()
