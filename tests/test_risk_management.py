# tests/test_risk_management.py
import unittest
from risk_management import compute_lot_size

class TestRiskManagement(unittest.TestCase):
    def test_compute_lot_size(self):
        """
        Tests that the lot size is computed correctly.
        """
        equity = 100000
        stop_loss_pips = 100
        lot_size = compute_lot_size(equity, stop_loss_pips)
        self.assertEqual(lot_size, 1.0)

    def test_compute_lot_size_with_zero_stop_loss(self):
        """
        Tests that the lot size is 0 if the stop loss is 0.
        """
        equity = 100000
        stop_loss_pips = 0
        lot_size = compute_lot_size(equity, stop_loss_pips)
        self.assertEqual(lot_size, 0.0)

if __name__ == '__main__':
    unittest.main()
