# utils.py
import logging
from logging.handlers import RotatingFileHandler
import os
import json
import subprocess
from datetime import datetime

LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name="next_to_me"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(os.path.join(LOG_DIR, f"{name}.log"), maxBytes=5_000_000, backupCount=5)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = get_logger()

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
