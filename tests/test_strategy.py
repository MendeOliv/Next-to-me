# tests/test_strategy.py
import unittest
import pandas as pd
from strategy import detect_price_action_entry

class TestStrategy(unittest.TestCase):
    def test_detect_price_action_entry(self):
        """
        Tests that the detect_price_action_entry function returns a dictionary with the expected keys.
        """
        df_15m = pd.DataFrame({'close': [1.0, 1.1, 1.2]})
        df_4h = pd.DataFrame({'close': [1.0, 1.1, 1.2]})
        signal = detect_price_action_entry(df_15m, df_4h)
        self.assertIsInstance(signal, dict)
        self.assertIn('is_entry', signal)

if __name__ == '__main__':
    unittest.main()
