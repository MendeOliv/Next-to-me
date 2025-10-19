# risk_management.py
from utils import logger
import json, os

STATE_FILE = os.environ.get("RISK_STATE_FILE", "risk_state.json")


def position_size(balance: float, risk_per_trade_pct: float, stop_loss_pips: float, pip_value: float) -> float:
    """Calcula o volume (lots/unidade) baseado em risco por trade (%), stop loss e pip value.

    Args:
        balance: saldo atual da conta (float)
        risk_per_trade_pct: risco por trade em porcentagem (ex: 1.0 para 1%)
        stop_loss_pips: stop loss em pips (deve ser > 0)
        pip_value: valor por pip (na unidade usada pelo ativo)

    Returns:
        volume (float)

    Raises:
        ValueError: se parâmetros inválidos.
    """
    if balance <= 0:
        raise ValueError("balance must be > 0")
    if risk_per_trade_pct <= 0:
        raise ValueError("risk_per_trade_pct must be > 0")
    if stop_loss_pips <= 0:
        raise ValueError("stop_loss_pips must be > 0")
    if pip_value <= 0:
        raise ValueError("pip_value must be > 0")

    # risk_per_trade_pct is expected as percentage (e.g., 1.0 == 1%)
    risk_amount = balance * (risk_per_trade_pct / 100.0)
    volume = risk_amount / (stop_loss_pips * pip_value)
    return float(volume)


def calculate_position_size(balance, stop_loss_pips, risk_percent):
    """Compatibilidade retroativa: aceita risk_percent como fração (0.02) ou porcentagem (2.0).

    Esta função será depreciada no futuro — use `position_size`.
    """
    # se risk_percent < 1 assume que é fração
    rp = float(risk_percent)
    if rp < 1.0:
        rp_pct = rp * 100.0
    else:
        rp_pct = rp
    try:
        # pip_value monetário por pip (ex.: 10.0)
        return round(position_size(float(balance), rp_pct, float(stop_loss_pips), float(os.environ.get("PIP_VALUE", 10.0))), 6)
    except Exception as e:
        logger.error(f"calculate_position_size error: {e}")
        return 0


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
