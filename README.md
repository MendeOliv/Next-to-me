# Next-to-me Trading Bot

## 1. Purpose

This project is a modular and optimized trading bot developed in Python, designed for the automation of trading strategies, backtesting, and preparation for use on proprietary trading platforms such as FTMO.

The bot is designed to interact with the MetaTrader 5 API and allows for backtesting of strategies using EURUSD OHLC data.

## 2. Features

- **Modularity**: The code is divided into independent modules for data handling, strategy, execution, and risk management.
- **Backtesting**: Allows for strategy testing with historical data, including simulation of transaction costs and slippage.
- **Live Trading**: Can connect to a MetaTrader 5 account to operate in real-time.
- **Risk Management**: Implements FTMO-style rules, such as maximum daily loss and maximum total loss.
- **Security**: Uses `.env` files for managing sensitive information, avoiding hardcoded keys in the code.

## 3. Installation and Environment Setup

### Prerequisites

- Python 3.10+
- MetaTrader 5 Terminal (for live trading)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Next-to-me
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```
    - **Windows:**
      ```bash
      .venv\Scripts\activate
      ```
    - **Linux/macOS:**
      ```bash
      source .venv/bin/activate
      ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    - Create a copy of `config.example.json` and rename it to `config.json`.
    - Create a `.env` file for sensitive data (e.g., account credentials).
    - An example `.env.example` file will be provided to show which variables are needed.

## 4. How to Use

The bot is executed from the command line through `main.py`.

### Parameters

-   `--mode`: Execution mode.
    -   `dryrun`: Runs a backtest with historical data.
    -   `live`: Operates in real-time with a MetaTrader 5 account.
-   `--data`: Path to the CSV file with historical data (required for `dryrun` mode).
-   `--config`: Path to the JSON configuration file (e.g., `config.json`).

### Examples

#### Backtesting (`dryrun`)

To run a backtest using a historical data file named `eurusd_15m.csv`:
```bash
python main.py --mode dryrun --data path/to/eurusd_15m.csv --config config.json
```

#### Live Trading (`live`)

To run the bot in live trading mode, connected to MetaTrader 5:
```bash
python main.py --mode live --config config.json
```
**Note:** Always test your strategies in a demo account before operating in a real account.

## 5. Project Structure

-   `main.py`: Main orchestrator of the bot.
-   `data_handler.py`: Module for importing, cleaning, and processing data.
-   `strategy.py`: Contains the trading logic and signal generation.
-   `execution.py`: Handles the simulated or real execution of orders.
-   `risk_management.py`: Manages risk, stop-loss, take-profit, and position sizing.
-   `mt5_connector.py`: Connects to the MetaTrader 5 API.
-   `utils.py`: Utility functions (logs, calculations, etc.).
-   `config.json`: Configuration file for the bot's parameters.
-   `.env`: File for environment variables (not versioned).
-   `requirements.txt`: List of project dependencies.
-   `tests/`: Directory with automated tests.
