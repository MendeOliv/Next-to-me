# Trading Bot EURUSD - FTMO rules (skeleton)

Projeto skeleton para bot de trading que opera externamente via MetaTrader5 Python API.

Estrutura de módulos:
- main.py: orquestrador principal (modo dryrun/backtest vs live)
- mt5_connector.py: inicializa MT5, envia ordens, consulta posições
- risk_engine.py: cálculo de MDL, MAXLOSS, sizing (1% por trade)
- order_manager.py: cria/fecha/modify ordens e trailing ATR
- signals.py: detectores price-action (placeholder, implementar regras)
- utils.py: funções utilitárias (ATR, pips/price conversion)
- backtest_eurusd_ftmo.py: backtester básico (15m) com regras FTMO (template)

Requisitos:
- Python 3.10+
- MetaTrader5 terminal (para modo live) e pacote `MetaTrader5` instalado

Como começar (local, VSCode):
1. Cria e abre pasta `trading_bot_project/` no VSCode.
2. Copia os ficheiros deste PR (ou desta conversa).
3. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
4. `pip install -r requirements.txt`
5. Para teste rápido (dryrun/backtest):
   `python main.py --mode dryrun --data path/to/eurusd_15m.csv`
6. Para live (após testar em demo): `python main.py --mode live`

Notas:
- O projeto é um esqueleto funcional. Implementa risk engine e integração MT5 básica.
- Implementa lógica ATR-based para trailing stops; signals.py tem detectores placeholder.
- Testa sempre em demo antes de ir real. FTMO rules (MDL, MaxLoss) são aplicadas no Risk Engine.
