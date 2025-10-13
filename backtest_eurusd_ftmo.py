#!/usr/bin/env python3
# backtest_eurusd_ftmo.py
# Template de backtest para EURUSD com regras FTMO + ATR trailing
# Requisitos (pip): pandas, numpy, ta, matplotlib
# Opcional: vectorbt, backtrader (para simulações mais realistas)
#
# Como usar:
# 1) Coloca um ficheiro CSV com candles OHLC em CSV com colunas:
#    ['datetime','open','high','low','close','volume']
#    datetime em ISO (ex: 2025-10-12 00:00:00)
# 2) python backtest_eurusd_ftmo.py --data eurusd_15m.csv --initial-balance 200000
#
# Nota: este script é um TEMPLATE; adaptações são esperadas para integrar dados de 4h e 15m
# e para converter pips/valor de pip conforme broker.

import argparse
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# try/except para dependências opcionais
try:
    import ta
except Exception:
    ta = None
    print("Aviso: pacote 'ta' não instalado. ATR será calculado manualmente se necessário.")

# -------------------------------
# Configurações
# -------------------------------
ACCOUNT_INITIAL_BALANCE = 200000.0
RISK_PER_TRADE = 0.01      # 1% por trade
MDL_PERCENT = 0.05         # 5% daily max loss
MAXLOSS_PERCENT = 0.10     # 10% total max loss
ATR_PERIOD = 14
ATR_MULTIPLIER_15M = 1.8
ATR_MULTIPLIER_4H = 3.0

PIP_VALUE_PER_STANDARD_LOT = 10.0  # EURUSD ~ $10 por pip por lot padrão

# Novas configurações da estratégia e custos
EMA_PERIOD_4H = 50         # Período da EMA para tendência no gráfico de 4H
EMA_PERIOD_15M = 21        # Período da EMA para entrada no gráfico de 15M
SPREAD_PIPS = 1.0          # Spread em pips a ser adicionado ao preço de entrada
COMMISSION_PER_LOT = 7.0   # Comissão em USD por lote padrão (ida e volta)

# -------------------------------
# Funções utilitárias
# -------------------------------
def load_csv(filepath):
    df = pd.read_csv(filepath, parse_dates=['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    return df

def compute_atr(df, period=14):
    # df must have columns: high, low, close
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr

def pips_to_price(pips):
    # 1 pip in EURUSD = 0.0001
    return pips * 0.0001

def price_to_pips(price_diff):
    return price_diff / 0.0001

def prepare_dataframes(df_15m):
    """Gera o Df de 4H e calcula indicadores para ambos."""
    # Garante que o datetime é o índice para reamostragem
    if not isinstance(df_15m.index, pd.DatetimeIndex):
        df_15m.set_index('datetime', inplace=True)

    # Reamostra 15m para 4h
    ohlc_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}
    df_4h = df_15m.resample('4h', origin='start_day').apply(ohlc_dict).dropna()

    # Calcula EMA 4H (tendência)
    if ta:
        df_4h[f'ema_{EMA_PERIOD_4H}'] = ta.trend.ema_indicator(df_4h['close'], window=EMA_PERIOD_4H)
    else: # Fallback manual
        df_4h[f'ema_{EMA_PERIOD_4H}'] = df_4h['close'].ewm(span=EMA_PERIOD_4H, adjust=False).mean()

    # Calcula EMA 15m (entrada)
    if ta:
        df_15m[f'ema_{EMA_PERIOD_15M}'] = ta.trend.ema_indicator(df_15m['close'], window=EMA_PERIOD_15M)
    else: # Fallback manual
        df_15m[f'ema_{EMA_PERIOD_15M}'] = df_15m['close'].ewm(span=EMA_PERIOD_15M, adjust=False).mean()

    # Retorna os dataframes com o índice resetado para uso no loop
    df_15m.reset_index(inplace=True)
    df_4h.reset_index(inplace=True)
    return df_15m, df_4h

# -------------------------------
# FTMO Simulator helpers
# -------------------------------
class FTMOAccount:
    def __init__(self, initial_balance):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.daily_pnl = 0.0
        self.start_of_day = None
        self.open_positions = []

    def update_equity(self, current_time):
        unrealized = sum([pos['unrealized'] for pos in self.open_positions])
        self.equity = self.balance + unrealized

    def reset_daily_if_needed(self, now):
        today = now.date()
        if self.start_of_day is None or self.start_of_day != today:
            self.daily_pnl = 0.0
            self.start_of_day = today

    def check_limits(self):
        MDL_value = self.initial_balance * MDL_PERCENT
        MAXLOSS_value = self.initial_balance * MAXLOSS_PERCENT
        if self.equity <= self.initial_balance - MAXLOSS_value:
            return 'MAXLOSS'
        if self.daily_pnl <= -MDL_value:
            return 'MDL'
        return 'OK'

# -------------------------------
# Estratégia de Negociação (EMA Crossover com filtro de tendência)
# -------------------------------
def detect_trade_signal(df_15m_slice, df_4h, current_time):
    """
    Estratégia:
    1. TENDÊNCIA (4H): close da vela 4H ANTERIOR > EMA -> tendência de alta
    2. ENTRADA (15M): close da vela 15M ANTERIOR < EMA E close da vela ATUAL > EMA -> sinal de compra
    O inverso para venda.
    """
    signal = {'is_entry': False}

    # --- Lógica de Tendência 4H ---
    # Encontra a vela de 4h correspondente à vela atual de 15m
    # A vela de 4h que contém a vela de 15m começa em ou antes do tempo da vela de 15m
    relevant_4h_candle = df_4h[df_4h['datetime'] <= current_time].iloc[-1]

    # Usa a vela 4h anterior para confirmar a tendência
    idx = df_4h.index[df_4h['datetime'] == relevant_4h_candle['datetime']].tolist()[0]
    if idx < 1:
        return signal # Não há vela anterior para análise

    prev_4h_candle = df_4h.iloc[idx-1]
    ema_4h_value = prev_4h_candle[f'ema_{EMA_PERIOD_4H}']

    is_bullish_trend = prev_4h_candle['close'] > ema_4h_value
    is_bearish_trend = prev_4h_candle['close'] < ema_4h_value

    # --- Lógica de Entrada 15M ---
    if len(df_15m_slice) < 2:
        return signal # Precisa de pelo menos duas velas

    last_15m = df_15m_slice.iloc[-1]
    prev_15m = df_15m_slice.iloc[-2]

    ema_15m_last = last_15m[f'ema_{EMA_PERIOD_15M}']
    ema_15m_prev = prev_15m[f'ema_{EMA_PERIOD_15M}']

    # Sinal de compra: tendência de alta E cruzamento da EMA de 15m para cima
    if is_bullish_trend and prev_15m['close'] < ema_15m_prev and last_15m['close'] > ema_15m_last:
        stop_pips = last_15m['atr'] / pips_to_price(1) * ATR_MULTIPLIER_15M
        signal = {
            'is_entry': True,
            'side': 'buy',
            'reason': f'Tendência 4H alta, cruzamento EMA 15M',
            'stop_pips': stop_pips
        }

    # Sinal de venda: tendência de baixa E cruzamento da EMA de 15m para baixo
    elif is_bearish_trend and prev_15m['close'] > ema_15m_prev and last_15m['close'] < ema_15m_last:
        stop_pips = last_15m['atr'] / pips_to_price(1) * ATR_MULTIPLIER_15M
        signal = {
            'is_entry': True,
            'side': 'sell',
            'reason': f'Tendência 4H baixa, cruzamento EMA 15M',
            'stop_pips': stop_pips
        }

    return signal

# -------------------------------
# Backtest loop (simplified)
# -------------------------------
def backtest(data_15m_path):
    df15_raw = load_csv(data_15m_path)
    df15, df4h = prepare_dataframes(df15_raw)
    df15['atr'] = compute_atr(df15, period=ATR_PERIOD)
    account = FTMOAccount(ACCOUNT_INITIAL_BALANCE)
    trades = []

    # Itera candles
    for i in range(ATR_PERIOD, len(df15)):
        candle = df15.iloc[i]
        now = candle['datetime']
        account.reset_daily_if_needed(now)
        account.update_equity(now)
        limits_status = account.check_limits()
        if limits_status != 'OK':
            # se MDL ou MAXLOSS atingido, não abrir novas trades
            # opcional: fechar posições
            # Neste template apenas regista e continua
            print(f"[{now}] Limite atingido: {limits_status}. Nenhuma nova ordem será aberta.")
            continue

        # Detect signal
        signal = detect_trade_signal(df15.iloc[:i+1], df4h, now)
        if signal.get('is_entry'):
            # calcula stop/lot
            stop_pips = signal['stop_pips']
            risk_amount = account.equity * RISK_PER_TRADE
            pip_value = PIP_VALUE_PER_STANDARD_LOT
            lot_size = risk_amount / (stop_pips * pip_value)
            lot_size = max(0.01, round(lot_size, 2))

            # --- Lógica de Execução de Ordem Realista ---
            # A entrada ocorre na abertura da vela SEGUINTE ao sinal.
            if i + 1 >= len(df15):
                continue # Não há próxima vela para entrar, ignora sinal

            next_candle = df15.iloc[i+1]
            entry_price = next_candle['open']
            entry_time = next_candle['datetime']

            initial_stop_price = entry_price - pips_to_price(stop_pips) if signal['side'] == 'buy' else entry_price + pips_to_price(stop_pips)
            pos = {
                'entry_time': entry_time,
                'entry_price': entry_price,
                'side': signal['side'],
                'lots': lot_size,
                'trailing_stop_price': initial_stop_price,
                'tp_price': entry_price + pips_to_price(signal.get('tp_pips', stop_pips * 2)) if signal['side'] == 'buy' else entry_price - pips_to_price(signal.get('tp_pips', stop_pips * 2)),
                'unrealized': 0.0
            }
            account.open_positions.append(pos)
            trades.append({'time': now, 'action': 'open', 'pos': pos})

        # Atualiza posições e trailing stops
        updated_positions = []
        for pos in account.open_positions:
            high = candle['high']
            low = candle['low']
            exit_price = None
            exit_reason = None

            # Lógica de verificação de saída e trailing stop
            if pos['side'] == 'buy':
                # Verifica se o stop foi atingido
                if low <= pos['trailing_stop_price']:
                    exit_price = pos['trailing_stop_price']
                    exit_reason = 'trailing_stop'
                # Verifica se o take profit foi atingido
                elif high >= pos['tp_price']:
                    exit_price = pos['tp_price']
                    exit_reason = 'tp'
                # Se não saiu, atualiza o trailing stop
                else:
                    current_atr_pips = candle['atr'] / pips_to_price(1) * ATR_MULTIPLIER_15M
                    new_stop_price = high - pips_to_price(current_atr_pips)
                    if new_stop_price > pos['trailing_stop_price']:
                        pos['trailing_stop_price'] = new_stop_price
            else:  # Venda
                # Verifica se o stop foi atingido
                if high >= pos['trailing_stop_price']:
                    exit_price = pos['trailing_stop_price']
                    exit_reason = 'trailing_stop'
                # Verifica se o take profit foi atingido
                elif low <= pos['tp_price']:
                    exit_price = pos['tp_price']
                    exit_reason = 'tp'
                # Se não saiu, atualiza o trailing stop
                else:
                    current_atr_pips = candle['atr'] / pips_to_price(1) * ATR_MULTIPLIER_15M
                    new_stop_price = low + pips_to_price(current_atr_pips)
                    if new_stop_price < pos['trailing_stop_price']:
                        pos['trailing_stop_price'] = new_stop_price

            if exit_price is not None:
                # --- Lógica de Custos de Negociação ---
                # 1. Spread
                price_diff = (exit_price - pos['entry_price']) if pos['side'] == 'buy' else (pos['entry_price'] - exit_price)
                pips_gross = price_to_pips(price_diff)
                pips_net = pips_gross - SPREAD_PIPS

                # 2. Comissão
                pnl_gross = pips_net * PIP_VALUE_PER_STANDARD_LOT * pos['lots']
                commission_cost = COMMISSION_PER_LOT * pos['lots']
                pnl_net = pnl_gross - commission_cost

                # Atualiza a conta com o PNL líquido
                account.balance += pnl_net
                account.daily_pnl += pnl_net
                trades.append({'time': now, 'action': 'close', 'pos': pos, 'exit_price': exit_price, 'pnl': pnl_net, 'reason': exit_reason})
            else:
                # Se a posição continua aberta, atualiza o PNL não realizado
                current_price = candle['close']
                price_diff = (current_price - pos['entry_price']) if pos['side'] == 'buy' else (pos['entry_price'] - current_price)
                pips = price_to_pips(price_diff)
                pos['unrealized'] = pips * PIP_VALUE_PER_STANDARD_LOT * pos['lots']
                updated_positions.append(pos)

        account.open_positions = updated_positions

    # Resumo
    final_balance = account.balance + sum([p['unrealized'] for p in account.open_positions])
    print("Backtest completo")
    print(f"Saldo inicial: {ACCOUNT_INITIAL_BALANCE}")
    print(f"Saldo final: {final_balance}")
    print(f"Trades: {len(trades)}")
    # Exportar trades para CSV
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df.to_csv('trades_backtest.csv', index=False)
        print("Trades exportados para trades_backtest.csv")
        print_performance_metrics(trades_df, ACCOUNT_INITIAL_BALANCE)
        plot_equity_curve(trades_df, ACCOUNT_INITIAL_BALANCE)
    else:
        print("Nenhuma transação foi executada.")

# -------------------------------
# Funções de Análise de Desempenho
# -------------------------------
def print_performance_metrics(trades_df, initial_balance):
    """Calcula e imprime as principais métricas de desempenho."""
    # Garante que a coluna 'pnl' é numérica
    trades_df['pnl'] = pd.to_numeric(trades_df['pnl'], errors='coerce')

    total_pnl = trades_df['pnl'].sum()
    gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
    gross_loss = trades_df[trades_df['pnl'] < 0]['pnl'].sum()
    total_trades = len(trades_df)

    winning_trades = trades_df[trades_df['pnl'] > 0]
    losing_trades = trades_df[trades_df['pnl'] < 0]

    win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
    loss_rate = (len(losing_trades) / total_trades) * 100 if total_trades > 0 else 0

    profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf')

    # Cálculo do Drawdown Máximo
    trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
    trades_df['equity'] = initial_balance + trades_df['cumulative_pnl']
    trades_df['running_max'] = trades_df['equity'].cummax()
    trades_df['drawdown'] = trades_df['running_max'] - trades_df['equity']
    max_drawdown = trades_df['drawdown'].max()

    print("\n--- Análise de Desempenho ---")
    print(f"Lucro/Prejuízo Total: ${total_pnl:,.2f}")
    print(f"Lucro Bruto: ${gross_profit:,.2f}")
    print(f"Prejuízo Bruto: ${gross_loss:,.2f}")
    print(f"Total de Transações: {total_trades}")
    print(f"Taxa de Sucesso: {win_rate:.2f}%")
    print(f"Taxa de Perda: {loss_rate:.2f}%")
    print(f"Fator de Lucro: {profit_factor:.2f}")
    print(f"Drawdown Máximo: ${max_drawdown:,.2f} ({max_drawdown/initial_balance:.2%})")

def plot_equity_curve(trades_df, initial_balance):
    """Gera e guarda o gráfico da curva de capital."""
    if 'equity' not in trades_df.columns:
        trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
        trades_df['equity'] = initial_balance + trades_df['cumulative_pnl']

    plt.figure(figsize=(12, 6))
    plt.plot(trades_df['time'], trades_df['equity'], label='Curva de Capital', color='blue')
    plt.title('Desempenho da Estratégia - Curva de Capital')
    plt.xlabel('Data')
    plt.ylabel('Capital da Conta ($)')
    plt.grid(True)
    plt.legend()
    plt.savefig('equity_curve.png')
    print("Gráfico da curva de capital guardado em 'equity_curve.png'")


# -------------------------------
# CLI
# -------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Caminho para CSV 15m')
    parser.add_argument('--initial-balance', type=float, default=ACCOUNT_INITIAL_BALANCE)
    args = parser.parse_args()
    ACCOUNT_INITIAL_BALANCE = args.initial_balance
    backtest(args.data)
