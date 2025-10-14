# risk_engine.py
from datetime import date
from typing import List
from utils import price_to_pips, pips_to_price

# Defaults (override by config if desired)
ACCOUNT_INITIAL_BALANCE = 200000.0
RISK_PER_TRADE = 0.01
MDL_PERCENT = 0.05
MAXLOSS_PERCENT = 0.10

class AccountState:
    def __init__(self, initial_balance: float = ACCOUNT_INITIAL_BALANCE):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.daily_pnl = 0.0
        self._day = date.today()
        self.open_positions = []  # list of dicts: {entry_price, lots, side, unrealized, ...}

    def reset_daily(self):
        if date.today() != self._day:
            self.daily_pnl = 0.0
            self._day = date.today()

    def update_equity(self):
        unreal = sum([p.get('unrealized', 0.0) for p in self.open_positions])
        self.equity = self.balance + unreal

    def mdl_value(self) -> float:
        return self.initial_balance * MDL_PERCENT

    def maxloss_value(self) -> float:
        return self.initial_balance * MAXLOSS_PERCENT

    def check_limits(self) -> str:
        """
        Return 'OK', 'MDL' or 'MAXLOSS'
        """
        if self.equity <= self.initial_balance - self.maxloss_value():
            return 'MAXLOSS'
        if self.daily_pnl <= -self.mdl_value():
            return 'MDL'
        return 'OK'

def compute_lot_size(equity: float, stop_loss_pips: float, pip_value_per_lot: float = 10.0, risk_per_trade: float = RISK_PER_TRADE, max_lot: float = 50.0) -> float:
    """
    lot_size = risk_amount / (stop_loss_pips * pip_value_per_lot)
    """
    risk_amount = equity * risk_per_trade
    if stop_loss_pips <= 0:
        return 0.0
    lot = risk_amount / (stop_loss_pips * pip_value_per_lot)
    lot = max(0.01, round(lot, 2))
    if lot > max_lot:
        lot = max_lot
    return lot
