# tests/test_data_handler.py
import unittest
import pandas as pd
from data_handler import load_historical_data

class TestDataHandler(unittest.TestCase):
    def test_load_historical_data(self):
        """
        Tests that historical data is loaded correctly from a CSV file.
        """
        df = load_historical_data("tests/dummy_data.csv")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

    def test_load_nonexistent_file(self):
        """
        Tests that the function handles a nonexistent file gracefully.
        """
        df = load_historical_data("nonexistent_file.csv")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()
