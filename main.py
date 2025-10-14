# main.py
import argparse
import sys
import backtest_eurusd_ftmo as bt

def run_backtest(data_csv):
    bt.backtest(data_csv)

def run_live():
    from mt5_connector import initialize, shutdown, account_info
    print("Inicializando MT5...")
    try:
        initialize()
    except Exception as e:
        print("Erro ao inicializar MT5:", e)
        return
    info = account_info()
    print("Account info:", info)
    # Aqui podes iniciar o loop de recolha de candles e execução de lógica
    # Exemplo minimo: obter taxas e imprimir
    shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['dryrun', 'live'], default='dryrun')
    parser.add_argument('--data', help='CSV 15m para dryrun/backtest')
    args = parser.parse_args()
    if args.mode == 'dryrun':
        if not args.data:
            print("Fornece --data para dryrun (path para CSV 15m).")
            sys.exit(1)
        run_backtest(args.data)
    else:
        run_live()
