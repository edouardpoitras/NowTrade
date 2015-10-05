import unittest
from nowtrade.trade import Trade

class TestTrade(unittest.TestCase):
    def test_trade(self):
        self.trade = Trade('DATETIME', 'ACTION', 'SYMBOL', 'PRICE', 'SHARES', 'MONEY', 'FEE', 'SLIPPAGE')
        self.assertEquals(self.trade.__repr__(), "Trade(['DATETIME', 'ACTION', 'SYMBOL', 'PRICE', 'SHARES', 'MONEY', 'FEE', 'SLIPPAGE'])")

if __name__ == "__main__":
    unittest.main()
