# main.py
import asyncio
from utils import logger
from config_loader import load_config
from core.engine import get_data, execute_trade
from signals.strategy import generate_signal
from risk_management import calculate_position_size
import pandas as pd

async def run_live(config):
    logger.info("Live mode starting.")
    while True:
        # A lógica de dados ao vivo ainda é um placeholder.
        # Numa implementação real, a chamada `get_data` seria assíncrona (`await get_data(...)`)
        # e usaria, por exemplo, aiohttp ou um cliente de websocket.
        logger.info("Fetching live data (placeholder)...")
        await asyncio.sleep(60) # Pausa assíncrona

def run_backtest(config):
    data = get_data(
        symbol=config['symbol'],
        timeframe=config['timeframe'],
        live=False
    )
    if data.empty:
        logger.error("No data for backtest. Exiting.")
        return

    results = []
    balance = config['initial_balance']

    for i in range(1, len(data)):
        df_slice = data.iloc[:i]
        signal = generate_signal(df_slice)
        if signal:
            result = execute_trade(
                signal, balance, config, config['strategy'], df_slice['close'].iloc[-1], live=False
            )
            results.append(result)
            balance = result.get('balance_after', balance)

    pd.DataFrame(results).to_csv('backtest_results.csv', index=False)
    logger.info("Backtest finished. Results saved to backtest_results.csv")

if __name__ == "__main__":
    try:
        cfg = load_config()

        if cfg['live_mode']:
            asyncio.run(run_live(cfg))
        else:
            run_backtest(cfg)

    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
