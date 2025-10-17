# Next-to-Me Trading Bot

Este é um robô de trading modular em Python, projetado para ser robusto, testável e seguro, ideal para ambientes de backtesting e preparação para `prop trading`.

## Arquitetura

O bot utiliza uma arquitetura modular e centralizada:

-   **`main.py`**: Ponto de entrada que orquestra os modos de execução (`backtest` ou `live`).
-   **`core/engine.py`**: O coração do bot, responsável por buscar dados e executar ordens.
-   **`signals/strategy.py`**: Módulo dedicado à geração de sinais de trading (atualmente, uma estratégia baseada em RSI).
-   **`risk_management.py`**: Gerencia o cálculo de tamanho de posição e o estado de risco da conta.
-   **`utils.py`**: Fornece um logger centralizado e outras funções auxiliares.
-   **`.env`**: Arquivo de configuração para todas as variáveis de ambiente (credenciais, modo de operação, etc.).
-   **`config.example.json`**: Arquivo de exemplo para configurações adicionais da estratégia e do backtest.

## Instruções de Uso

### 1. Configuração do Ambiente

a. **Clone o Repositório:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```

b. **Crie o Ambiente Virtual e Instale as Dependências:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

c. **Configure as Variáveis de Ambiente:**
   - Crie uma cópia do arquivo `.env.example` e renomeie para `.env`.
   - Preencha o `.env` com suas configurações. As variáveis principais são:
     ```env
     # --- Modo de Operação ---
     LIVE_MODE=False               # Defina como 'True' para execução real/paper trading

     # --- Configurações da Estratégia e Risco ---
     RISK_PERCENT=0.02             # Risco por trade (ex: 0.02 para 2%)
     SYMBOL=EURUSD                 # Símbolo do instrumento
     TIMEFRAME=15m                 # Timeframe para análise

     # --- Caminhos e Logs ---
     LOG_DIR=logs                  # Diretório para salvar os arquivos de log
     DATA_PATH=dummy_data.csv      # Caminho para o arquivo CSV com dados históricos para backtest

     # --- Credenciais (para Modo Live) ---
     API_KEY=
     API_SECRET=
     ```

### 2. Executando em Modo Backtest

O modo backtest simula a estratégia com base em dados históricos de um arquivo CSV.

a. **Prepare seus Dados:**
   - Garanta que o arquivo CSV definido em `DATA_PATH` (no `.env`) exista.
   - O arquivo deve conter pelo menos uma coluna `timestamp` e uma coluna `close`.

b. **Execute o Backtest:**
   - Certifique-se de que `LIVE_MODE` em seu `.env` está definido como `False`.
   - Rode o bot a partir do seu terminal:
     ```bash
     python main.py
     ```
   - Ao final da execução, um arquivo `backtest_results.csv` será gerado na raiz do projeto com os detalhes de cada operação simulada.

### 3. Executando em Modo Live

O modo `live` é projetado para operar em tempo real, mas a lógica de busca de dados contínua (via websocket ou polling) é um **esqueleto** e precisa ser implementada.

a. **Configure para Live:**
   - No arquivo `.env`, mude `LIVE_MODE` para `True`.
   - Preencha as credenciais de API (`API_KEY`, `API_SECRET`, etc.).

b. **Execute o Robô:**
   ```bash
   python main.py
   ```
   - O bot iniciará no modo `live`, mas a lógica de loop contínuo em `run_live()` precisa ser desenvolvida para se conectar à sua fonte de dados em tempo real.

## Testes

Para validar a funcionalidade dos módulos, você pode executar os testes unitários com `pytest`:

```bash
pytest
```
**Nota:** A execução dos testes pode falhar em ambientes não-Windows devido à dependência `MetaTrader5`.

## Próximos Passos (Desenvolvimento)

-   **Integrar `risk_management.py`**: A função `calculate_position_size` precisa ser chamada em `core/engine.py` para que o lote seja calculado dinamicamente.
-   **Finalizar `run_live`**: Implementar a busca de dados em tempo real (ex: usando `ccxt`, `MetaTrader5`, ou outra API) dentro do loop `while` em `run_live()` em `main.py`.
-   **Unificar Configurações**: Centralizar todas as configurações (atualmente divididas entre `.env` e `config.example.json`) em uma única fonte para maior clareza.
