# backtest_eurusd_ftmo.py
import pandas as pd
from utils import compute_atr, pips_to_price, price_to_pips
from risk_engine import ACCOUNT_INITIAL_BALANCE, RISK_PER_TRADE, MDL_PERCENT, MAXLOSS_PERCENT

class FTMOBacktester:
    def __init__(self, df_15m: pd.DataFrame):
        self.df = df_15m.copy()
        self.df['atr'] = compute_atr(self.df)
        self.initial_balance = ACCOUNT_INITIAL_BALANCE
        self.balance = self.initial_balance
        self.open_positions = []
        self.trades = []
        self.daily_pnl = 0.0
        self.start_of_day = None

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
        for i in range(14, len(self.df)):
            candle = self.df.iloc[i]
            now = candle['datetime']
            self.reset_daily_if_needed(now)
            status = self.check_limits()
            if status != 'OK':
                # stop opening new trades for this day / overall
                continue
            # Placeholder: no trading logic implemented here yet.
            # Could call signals.detect_price_action_entry and then open positions
            pass

        # summary
        final_balance = self.balance + sum([p.get('unrealized', 0.0) for p in self.open_positions])
        return {
            "initial_balance": self.initial_balance,
            "final_balance": final_balance,
            "n_trades": len(self.trades)
        }

def backtest(path_to_csv: str):
    df = pd.read_csv(path_to_csv, parse_dates=['datetime'])
    bt = FTMOBacktester(df)
    res = bt.run()
    print("Backtest result (template):", res)
