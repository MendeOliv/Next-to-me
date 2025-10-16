# main.py
import json, os, time
from utils import logger, git_hash, save_trades_csv, save_summary
from data_handler import load_csv_data
from strategy import generate_sma_signals
from execution import SimulatedExecution, LiveExecution
from mt5_connector import MT5Connector
from risk_management import position_size, load_risk_state, save_risk_state
from analysis import compute_metrics

def watchdog_check(state, config):
    if state.get("daily_loss_pct", 0.0) >= config['risk']['max_daily_loss_pct']:
        logger.error("Max daily loss exceeded. Shutting down.")
        return False
    if state.get("total_drawdown_pct", 0.0) >= config['risk']['max_total_loss_pct']:
        logger.critical("Max total loss exceeded. Shutting down permanently.")
        return False
    return True

def load_config(path="config.example.json"):
    with open(path, "r") as f:
        return json.load(f)

def run_backtest(config):
    df = load_csv_data(config['data']['path'])
    signals = generate_sma_signals(df, short_window=config['strategy']['short_window'], long_window=config['strategy']['long_window'])
    execu = SimulatedExecution(
        slippage_pips=config['execution']['slippage_pips'],
        spread_pips=config['execution']['spread_pips'],
        pip_value=config['execution']['pip_value'],
        latency_ms=config['execution'].get('latency_ms', 100)
    )
    state = load_risk_state()
    trades = []
    balance = config['initial_balance']
    for idx, row in signals.iterrows():
        if row['signal_change'] == 1:
            sl = row['close'] - config['strategy']['stop_loss_pips'] * config['execution']['pip_value']
            size = position_size(balance, config['risk']['risk_per_trade_pct'], config['strategy']['stop_loss_pips'], config['execution']['pip_value'])
            trade = execu.place_order(config['instrument'], "buy", size, price=row['close'], sl=sl, tp=None)
            trades.append({**trade, "timestamp": idx.isoformat(), "balance_before": balance})
            exit_price = trade['entry_price'] + config['strategy'].get('take_profit_pips', 0) * config['execution']['pip_value']
            pnl = (exit_price - trade['entry_price']) * size * (1/config['execution']['pip_value'])
            balance += pnl
            trades[-1].update({"exit_price": exit_price, "pnl": pnl, "balance_after": balance})
            state['balance'] = balance
        state['daily_loss_pct'] = max(0, (config['initial_balance'] - balance) / config['initial_balance'] * 100)
        if not watchdog_check(state, config):
            logger.error("Watchdog stopped backtest")
            break

    metrics = compute_metrics(trades, config['initial_balance'])
    summary = {
        "final_balance": balance,
        "trades": len(trades),
        "git_hash": git_hash(),
        **metrics
    }
    save_trades_csv(trades)
    save_summary(summary)
    save_risk_state(state)

def run_live(config):
    conn = MT5Connector(login=os.environ.get("MT5_LOGIN"), password=os.environ.get("MT5_PASS"), server=os.environ.get("MT5_SERVER"))
    execu = LiveExecution(conn)
    logger.info("Run live not fully implemented in this skeleton")
    # TODO: Implementar loop principal com subscrição de preços em tempo real
    return

if __name__ == "__main__":
    cfg = load_config(os.environ.get("CONFIG_PATH", "config.example.json"))
    mode = cfg.get("mode", "backtest")
    if mode == "backtest":
        run_backtest(cfg)
    else:
        run_live(cfg)
