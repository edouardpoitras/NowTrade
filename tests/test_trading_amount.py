"""
Tests for trading_amount.py module.
"""
import unittest
from nowtrade.trading_amount import NumberOfShares, CapitalPercentage, KellyCriterion

class TestTradingAmount(unittest.TestCase):
    """
    Tests trading_amount.py classes.
    """
    def test_trading_amount(self):
        """
        Simple test for all trading amounts.
        """
        trading_amount = NumberOfShares(1)
        self.assertEquals(trading_amount.get_shares(100, 1000), 1)
        trading_amount = CapitalPercentage(50)
        self.assertEquals(trading_amount.get_shares(100, 1000), 5)
        trading_amount = KellyCriterion(50, 0.5, 0.5)
        self.assertEquals(trading_amount.get_shares(100, 1000), 99000)

if __name__ == "__main__":
    unittest.main()
