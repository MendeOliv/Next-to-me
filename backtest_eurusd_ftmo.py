# backtest_eurusd_ftmo.py
import pandas as pd
from utils import get_logger
from data_handler import load_csv_data
from strategy import generate_signals
from execution import simulate_order_fill, log_trade
from risk_management import position_size

logger = get_logger("backtester")

def backtest(path_to_csv: str, config: dict):
    df = load_csv_data(path_to_csv)
    params = config.get('strategy_params', {'short_window': 50, 'long_window': 200})
    signals = generate_signals(df, params)

    balance = config['initial_balance']
    trades = []

    for i in range(1, len(signals)):
        if signals['positions'][i] == 1.0: # Buy signal
            stop_loss_pips = 100 # Example stop loss
            lot_size = position_size(balance, config['risk']['risk_per_trade_pct'], stop_loss_pips, config['execution']['pip_value'])

            entry_price = df['open'][i]
            fill_price = simulate_order_fill(entry_price, 'buy', lot_size, **config['execution'])

            # For simplicity, close on the next candle
            exit_price = df['open'][i+1] if i+1 < len(df) else df['close'][i]
            pnl = (exit_price - fill_price) * lot_size * 100000 # Simplified PnL
            balance += pnl

            trade_data = {
                "timestamp": signals.index[i],
                "order_id": len(trades) + 1,
                "side": "buy",
                "volume": lot_size,
                "entry_price": fill_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "balance_after": balance,
                "reason": "MA Crossover"
            }
            log_trade(trade_data)
            trades.append(trade_data)

    logger.info(f"Backtest complete. Final balance: {balance}")
    return trades
