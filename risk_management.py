# risk_management.py
from utils import logger
import json, os

STATE_FILE = os.environ.get("RISK_STATE_FILE", "risk_state.json")

def position_size(balance, risk_per_trade_pct, stop_loss_pips, pip_value, lot_unit_scale=1.0):
    """
    balance: capital disponível
    risk_per_trade_pct: % do balance a arriscar por trade (ex: 1.0)
    stop_loss_pips: pips até stop loss (positivo)
    pip_value: USD por pip para 1 lote padrão
    lot_unit_scale: escala - por padrão 1.0 => retorno em lotes padrão
    """
    if stop_loss_pips <= 0:
        logger.error("stop_loss_pips must be > 0")
        raise ValueError("stop_loss_pips must be > 0")
    risk_amount = balance * (risk_per_trade_pct / 100.0)
    volume = risk_amount / (stop_loss_pips * pip_value)
    volume = volume * lot_unit_scale
    return max(round(volume, 4), 0.0001)

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
