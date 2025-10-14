# backtest_eurusd_ftmo.py
import pandas as pd
import logging
import random
from utils import compute_atr, pips_to_price, price_to_pips
from risk_management import ACCOUNT_INITIAL_BALANCE, RISK_PER_TRADE, MDL_PERCENT, MAXLOSS_PERCENT, TRANSACTION_COST_PIPS
from data_handler import load_historical_data

class FTMOBacktester:
    def __init__(self, df_15m: pd.DataFrame, transaction_cost_pips: float = TRANSACTION_COST_PIPS, slippage_pips: float = 0.1):
        self.df = df_15m.copy()
        self.df['atr'] = compute_atr(self.df)
        self.initial_balance = ACCOUNT_INITIAL_BALANCE
        self.balance = self.initial_balance
        self.open_positions = []
        self.trades = []
        self.daily_pnl = 0.0
        self.start_of_day = None
        self.transaction_cost = pips_to_price(transaction_cost_pips)
        self.slippage_pips = slippage_pips
        self.peak_equity = self.initial_balance
        self.max_drawdown = 0.0

    def reset_daily_if_needed(self, now):
        today = pd.to_datetime(now).date()
        if self.start_of_day is None or self.start_of_day != today:
            self.daily_pnl = 0.0
            self.start_of_day = today

    def check_limits(self):
        MDL_value = self.initial_balance * MDL_PERCENT
        MAXLOSS_value = self.initial_balance * MAXLOSS_PERCENT
        equity = self.balance + sum([p.get('unrealized', 0.0) for p in self.open_positions])
        if equity <= self.initial_balance - MAXLOSS_value:
            return 'MAXLOSS'
        if self.daily_pnl <= -(self.initial_balance * MDL_PERCENT):
            return 'MDL'
        return 'OK'

    def run(self):
        # Template loop: no signal logic included. Replace detect logic as needed.
        for i in range(14, len(self.df) - 1):
            candle = self.df.iloc[i]
            now = candle['datetime']
            self.reset_daily_if_needed(now)
            status = self.check_limits()
            if status != 'OK':
                # stop opening new trades for this day / overall
                continue

            # Placeholder trading logic: open a trade and close it on the next candle
            if not self.open_positions:
                slippage = random.uniform(-self.slippage_pips, self.slippage_pips)
                entry_price = self.df.iloc[i + 1]['open'] + pips_to_price(slippage)

                trade = {
                    'entry_price': entry_price,
                    'exit_price': self.df.iloc[i + 1]['close'] + pips_to_price(random.uniform(-self.slippage_pips, self.slippage_pips)),
                    'side': 'buy',
                    'entry_time': now,
                    'exit_time': self.df.iloc[i + 1]['datetime'],
                }

                pnl = (trade['exit_price'] - trade['entry_price']) - self.transaction_cost
                self.balance += pnl
                self.daily_pnl += pnl
                self.trades.append(trade)

                # Update equity and calculate drawdown
                equity = self.balance
                self.peak_equity = max(self.peak_equity, equity)
                drawdown = (self.peak_equity - equity) / self.peak_equity
                self.max_drawdown = max(self.max_drawdown, drawdown)

        # summary
        final_balance = self.balance
        total_return = (final_balance - self.initial_balance) / self.initial_balance

        if self.trades:
            returns = pd.Series([t['exit_price'] - t['entry_price'] for t in self.trades])
            sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
            win_rate = (returns > 0).mean()
        else:
            sharpe_ratio = 0
            win_rate = 0

        return {
            "initial_balance": self.initial_balance,
            "final_balance": final_balance,
            "n_trades": len(self.trades),
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "max_drawdown": self.max_drawdown,
        }

def backtest(path_to_csv: str):
    df = load_historical_data(path_to_csv)
    bt = FTMOBacktester(df)
    res = bt.run()
    logging.info(f"Backtest result: {res}")
