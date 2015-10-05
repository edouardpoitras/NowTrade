import unittest
from nowtrade.trading_amount import NumberOfShares, CapitalPercentage, KellyCriterion

class TestTradingAmount(unittest.TestCase):
    def test_number_of_shares(self):
        self.trading_amount = NumberOfShares(1)
        self.assertEquals(self.trading_amount.get_shares(100, 1000), 1)
        self.trading_amount = CapitalPercentage(50)
        self.assertEquals(self.trading_amount.get_shares(100, 1000), 5)
        self.trading_amount = KellyCriterion(50, 0.5, 0.5)
        self.assertEquals(self.trading_amount.get_shares(100, 1000), 99000)

if __name__ == "__main__":
    unittest.main()
