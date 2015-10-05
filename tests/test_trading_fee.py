"""
Tests for trading_fee.py module.
"""
import unittest
from nowtrade.trading_fee import StaticFee

class TestTradingFees(unittest.TestCase):
    """
    Tests trading_fee.py classes.
    """
    def test_trading_fees(self):
        """
        Simple test for all trading fees.
        """
        trading_fee = StaticFee(5)
        self.assertEquals(trading_fee.get_fee(100, 1), 5)

if __name__ == "__main__":
    unittest.main()
