"""
Tests for trading_amount.py module.
"""
import unittest
from nowtrade.trading_amount import StaticAmount, NumberOfShares, CapitalPercentage, KellyCriterion

class TestTradingAmount(unittest.TestCase):
    """
    Tests trading_amount.py classes.
    """
    def test_trading_amount(self):
        """
        Simple test for all trading amounts.
        """
        trading_amount = StaticAmount(5, round_up=True)
        self.assertEquals(trading_amount.__repr__(), 'StaticAmount(amount=5, round_up=True)')
        self.assertEquals(trading_amount.get_shares(1, 5), 5)
        trading_amount = NumberOfShares(1)
        self.assertEquals(trading_amount.__repr__(), 'NumberOfShares(shares=1)')
        self.assertEquals(trading_amount.get_shares(100, 1000), 1)
        trading_amount = CapitalPercentage(50)
        self.assertEquals(trading_amount.__repr__(), 'CapitalPercentage(percent=50)')
        self.assertEquals(trading_amount.get_shares(100, 1000), 5)
        trading_amount = KellyCriterion(50, 0.5, 0.5)
        self.assertEquals(trading_amount.__repr__(), 'KellyCriterion(win_probability=50, average_gains=0.5, average_losses=0.5)')
        self.assertEquals(trading_amount.get_shares(100, 1000), 99000)

if __name__ == "__main__":
    unittest.main()
