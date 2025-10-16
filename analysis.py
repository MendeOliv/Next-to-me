# analysis.py
import numpy as np

def compute_metrics(trades, initial_balance):
    pnl_list = [t.get('pnl', 0) for t in trades]
    returns = np.array(pnl_list) / initial_balance
    total_return = sum(pnl_list)
    win_rate = sum(1 for p in pnl_list if p > 0) / max(1, len(pnl_list))
    avg_win = np.mean([p for p in pnl_list if p > 0]) if any(p > 0 for p in pnl_list) else 0
    avg_loss = np.mean([p for p in pnl_list if p < 0]) if any(p < 0 for p in pnl_list) else 0
    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }
