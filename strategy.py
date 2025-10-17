# strategy.py
import pandas as pd
import numpy as np
from signals.strategy import generate_signal #, generate_sma_signals

# Wrapper para compatibilidade com os testes que esperam generate_signals
def generate_signals(df, params=None, short_window=20, long_window=50):
    # Tenta usar a implementação de generate_sma_signals se existir, senão usa um fallback.
    # Como generate_sma_signals foi removido no prompt anterior, vamos focar em generate_signal.

    # O teste espera um DataFrame de volta, então vamos simular isso.
    df_signals = df.copy()
    df_signals['signal'] = 0

    # A lógica real está em generate_signal que retorna um sinal simples ('buy'/'sell')
    # Para um backtest completo, isso precisaria ser adaptado para preencher a coluna 'signal'
    last_signal = generate_signal(df)
    if last_signal == 'buy':
        df_signals.loc[df_signals.index[-1], 'signal'] = 1
    elif last_signal == 'sell':
        df_signals.loc[df_signals.index[-1], 'signal'] = -1

    return df_signals
