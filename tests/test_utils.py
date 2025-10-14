# tests/test_utils.py
import unittest
from utils import price_to_pips, pips_to_price

class TestUtils(unittest.TestCase):
    def test_price_to_pips(self):
        """
        Tests that the price is converted to pips correctly.
        """
        pips = price_to_pips(0.0001)
        self.assertEqual(pips, 1)

    def test_pips_to_price(self):
        """
        Tests that pips are converted to price correctly.
        """
        price = pips_to_price(1)
        self.assertEqual(price, 0.0001)

if __name__ == '__main__':
    unittest.main()
