# tests/test_data_handler.py
import pandas as pd
from data_handler import load_csv_data

def test_load_csv_data(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text("timestamp,open,high,low,close\n2025-01-01 00:00,1.1,1.2,1.0,1.15\n")
    df = load_csv_data(str(p))
    assert isinstance(df, pd.DataFrame)
    assert df['close'].iloc[0] == 1.15
