# risk_management.py
from utils import logger
import json, os

STATE_FILE = os.environ.get("RISK_STATE_FILE", "risk_state.json")

def calculate_position_size(balance, stop_loss_pips, risk_percent):
    if stop_loss_pips <= 0:
        logger.error("stop_loss_pips deve ser > 0")
        return 0
    risk_amount = balance * risk_percent
    position_size = risk_amount / stop_loss_pips
    return round(position_size, 2)

def position_size(balance, risk_per_trade_pct, stop_loss_pips, pip_value):
    if stop_loss_pips <= 0:
        raise ValueError('stop_loss_pips must be > 0')
    risk_amount = balance * (risk_per_trade_pct / 100.0)
    volume = risk_amount / (stop_loss_pips * pip_value)
    return volume

def load_risk_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load risk state: {e}")
    return {"balance": None, "peak_balance": None, "daily_loss": 0.0, "total_drawdown_pct": 0.0}

def save_risk_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        logger.error(f"Failed to save risk state: {e}")
