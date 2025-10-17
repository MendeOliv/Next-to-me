# core/engine.py
import os
import pandas as pd
from utils import logger
from mt5_connector import MT5Connector
from execution import SimulatedExecution
from risk_management import calculate_position_size

# --- Data Fetching ---
def fetch_historical_data(symbol, timeframe, start=None, end=None):
    """Carrega dados de um arquivo CSV, em vez de uma API de exemplo."""
    data_path = os.getenv('DATA_PATH', 'dummy_data.csv')
    logger.info(f"Loading historical data from {data_path}")
    try:
        df = pd.read_csv(data_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            df.set_index('timestamp', inplace=True)
        return df.sort_index()
    except FileNotFoundError:
        logger.error(f"Data file not found at {data_path}")
        return pd.DataFrame()

def get_data(symbol, timeframe, start=None, end=None, live=False):
    if live:
        # A lógica de dados ao vivo será tratada no loop principal via MT5Connector
        logger.warning("Live data fetching in get_data is a placeholder.")
        return pd.DataFrame()
    else:
        return fetch_historical_data(symbol, timeframe, start, end)

# --- Trade Execution ---
def simulate_trade(signal, balance, config, strategy_config, current_price):
    """Executa uma simulação de trade usando a lógica de SimulatedExecution."""
    exec_params = config['execution']
    sim_exec = SimulatedExecution(
        slippage_pips=exec_params['slippage_pips'],
        spread_pips=exec_params['spread_pips'],
        pip_value=exec_params['pip_value']
    )

    stop_loss_pips = strategy_config['stop_loss_pips']
    risk_percent = config['risk']['risk_per_trade_pct']
    size = calculate_position_size(balance, stop_loss_pips, risk_percent)

    trade_result = sim_exec.place_order(
        instrument=config['instrument'],
        side=signal,
        volume=size,
        price=current_price,
        sl=current_price - stop_loss_pips * exec_params['pip_value'] if signal == 'buy' else current_price + stop_loss_pips * exec_params['pip_value']
    )

    # Simulação de saída (ex: take profit ou stop loss)
    exit_price = 0
    if signal == 'buy':
        exit_price = trade_result['entry_price'] + strategy_config.get('take_profit_pips', 100) * exec_params['pip_value']
    else: # Sell
        exit_price = trade_result['entry_price'] - strategy_config.get('take_profit_pips', 100) * exec_params['pip_value']

    pnl = (exit_price - trade_result['entry_price']) * size * (1 / exec_params['pip_value']) if signal == 'buy' else (trade_result['entry_price'] - exit_price) * size * (1 / exec_params['pip_value'])
    trade_result['pnl'] = pnl
    trade_result['balance_after'] = balance + pnl

    return trade_result

def send_order(signal, balance, risk_config, strategy_config, current_price):
    """Envia uma ordem real usando o MT5Connector."""
    connector = MT5Connector() # Conecta usando variáveis de ambiente
    connector.connect() # Garante que a conexão está ativa

    stop_loss_pips = strategy_config['stop_loss_pips']
    size = calculate_position_size(balance, stop_loss_pips, risk_config['risk']['risk_per_trade_pct'])

    sl = current_price - stop_loss_pips * risk_config['execution']['pip_value'] if signal == 'buy' else current_price + stop_loss_pips * risk_config['execution']['pip_value']

    return connector.place_order(
        instrument=risk_config['instrument'],
        side=signal,
        volume=size,
        price=current_price,
        sl=sl
    )

def execute_trade(signal, balance, risk_config, strategy_config=None, current_price=None, live=False):
    # Backwards-compatible wrapper: tests may pass risk_config as a float (risk percent)
    if isinstance(risk_config, (int, float)):
        # if <1 assume fraction, convert to percent
        risk_conf = {'risk_per_trade_pct': float(risk_config)*100 if risk_config < 1.0 else float(risk_config)}
    else:
        risk_conf = risk_config or {}
    # ensure execution defaults & instrument
    risk_conf.setdefault('execution', {'pip_value': 10.0, 'slippage_pips': 1.0, 'spread_pips': 0.1})
    risk_conf.setdefault('instrument', 'EURUSD')
    if strategy_config is None:
        strategy_config = {'stop_loss_pips': float(os.getenv('DEFAULT_STOP_LOSS_PIPS', 50))}
    if current_price is None:
        current_price = float(os.getenv('DEFAULT_PRICE', 1.0))
    if live:
        return send_order(signal, balance, risk_conf, strategy_config, current_price)
    else:
        return simulate_trade(signal, balance, risk_conf, strategy_config, current_price)
# --- Async wrappers for integration with asyncio loops ---
async def async_get_data(symbol, timeframe, start=None, end=None, live=False):
    """
    Async wrapper around get_data / fetch_historical_data.
    Uses asyncio.to_thread to run blocking pandas IO in a thread.
    """
    return await asyncio.to_thread(get_data, symbol, timeframe, start, end, live)

async def async_simulate_trade(signal, balance, config, strategy_config, current_price):
    """Async wrapper for simulate_trade"""
    return await asyncio.to_thread(simulate_trade, signal, balance, config, strategy_config, current_price)

async def async_send_order(signal, balance, risk_config, strategy_config, current_price):
    """Async wrapper for send_order (MT5 live wrapper)"""
    return await asyncio.to_thread(send_order, signal, balance, risk_config, strategy_config, current_price)

async def async_execute_trade(signal, balance, risk_config, strategy_config=None, current_price=None, live=False):
    """
    Async wrapper for execute_trade.
    Keeps behaviour identical; just runs in thread to avoid blocking.
    """
    return await asyncio.to_thread(execute_trade, signal, balance, risk_config, strategy_config, current_price, live)
