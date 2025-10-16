# main.py
import json, os, time
import pandas as pd
from dotenv import load_dotenv
from utils import logger, save_trades_csv
from core.engine import get_data, execute_trade
from signals.strategy import generate_signal
from risk_management import calculate_position_size

load_dotenv()

def run_backtest():
    config_path = os.getenv('CONFIG_PATH', 'config.example.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    data = get_data(
        symbol=os.getenv('SYMBOL'),
        timeframe=os.getenv('TIMEFRAME'),
        live=False
    )
    if data.empty:
        logger.error("No data for backtest. Exiting.")
        return

    results = []
    balance = float(os.getenv('INITIAL_BALANCE', 10000))
    risk_percent = float(os.getenv('RISK_PERCENT', 0.02))

    for i in range(1, len(data)):
        df_slice = data.iloc[:i]
        signal = generate_signal(df_slice)
        if signal:
            result = execute_trade(
                signal, balance, config, config['strategy'], df_slice['close'].iloc[-1], live=False
            )
            results.append(result)
            balance = result.get('balance_after', balance)

    save_trades_csv(results)
    logger.info("Backtest finished.")

def run_live():
    logger.info("Live mode starting.")
    # A lógica de execução ao vivo foi simplificada para focar na estrutura.
    # A implementação completa exigiria um loop de polling ou websocket.
    while True:
        # Placeholder para a lógica de dados ao vivo
        time.sleep(60)

if __name__ == "__main__":
    live_mode = os.getenv('LIVE_MODE', 'False').lower() in ('true', '1', 't')

    if live_mode:
        run_live()
    else:
        run_backtest()
