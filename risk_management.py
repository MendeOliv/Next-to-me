# risk_management.py
from datetime import date
from typing import List
from utils import get_logger, price_to_pips, pips_to_price
import json
import os

logger = get_logger("risk_management")

def position_size(balance, risk_per_trade_pct, stop_loss_pips, pip_value):
    risk_amount = balance * (risk_per_trade_pct / 100.0)
    if stop_loss_pips <= 0:
        logger.error("stop_loss_pips must be > 0")
        raise ValueError("stop_loss_pips must be > 0")
    volume = risk_amount / (stop_loss_pips * pip_value)
    return max(volume, 0.0001)

def load_risk_state(filepath="risk_state.json"):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            state = json.load(f)
            logger.info("Risk state loaded.")
            return state
    logger.warning("No risk state file found. Starting fresh.")
    return {"balance": 0, "max_drawdown": 0, "daily_loss": 0, "daily_loss_pct": 0, "total_drawdown_pct": 0}

def save_risk_state(state, filepath="risk_state.json"):
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=4)
    logger.info("Risk state saved.")

class AccountState:
    def __init__(self, initial_balance: float):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.daily_pnl = 0.0
        self._day = date.today()
        self.open_positions = []

    def reset_daily(self):
        if date.today() != self._day:
            self.daily_pnl = 0.0
            self._day = date.today()
            logger.info("Resetting daily PnL.")

    def update_equity(self):
        unreal = sum([p.get('unrealized', 0.0) for p in self.open_positions])
        self.equity = self.balance + unreal
        logger.debug(f"Equity updated to: {self.equity}")
