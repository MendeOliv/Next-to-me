# utils.py
import logging
from logging.handlers import RotatingFileHandler
import os
import json
import subprocess
import uuid
from datetime import datetime

RUN_ID = os.environ.get("RUN_ID") or uuid.uuid4().hex[:8]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str = "next_to_me") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    fh = RotatingFileHandler(os.path.join(LOG_DIR, f"{name}.log"), maxBytes=5_000_000, backupCount=5)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(run_id)s | %(message)s")

    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.run_id = RUN_ID
            return True

    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addFilter(ContextFilter())
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_run_logger(name: str = "next_to_me") -> logging.Logger:
    """Helper que retorna um logger já configurado com run metadata.

    Uso: logger = get_run_logger(__name__)
    """
    log = get_logger(name)
    try:
        gh = git_hash()
    except Exception:
        gh = "unknown"
    log = logging.LoggerAdapter(log, {"git_hash": gh, "run_id": RUN_ID})
    return log

logger = get_run_logger()

def save_trades_csv(trades, out_dir="runs"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"run_{ts}_trades.csv")
    import csv
    if not trades:
        logger.warning("save_trades_csv called with empty trades")
        return None
    keys = list(trades[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(trades)
    logger.info(f"Saved trades to {path}")
    return path

def save_summary(summary: dict, out_dir="runs"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"run_{ts}_summary.json")
    with open(path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Saved summary to {path}")
    return path

def git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"
