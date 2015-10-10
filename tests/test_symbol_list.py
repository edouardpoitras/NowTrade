import unittest
from nowtrade.logger import CRITICAL
from nowtrade.symbol_list import SymbolList, StockList

class TestSymbolList(unittest.TestCase):
    def test_symbol_list(self):
        sanity = ['MSFT', 'GOOG', 'AAPL']
        symbols = ['msft', 'gOOg', 'AAPl']
        stocks = symbols
        symbol_list = SymbolList(symbols)
        symbol_list.logger.set_console_level(CRITICAL)
        stock_list = StockList(stocks)
        for symbol in symbol_list: sanity.remove(str(symbol))
        self.assertEqual(len(sanity), 0)
        msft = symbol_list.get('msft')
        goog = symbol_list.get('goog')
        self.assertEqual(msft.symbol, 'MSFT')
        self.assertEqual(msft.symbol, 'MSFT')
        self.assertEqual(msft.open, 'MSFT_Open')
        self.assertEqual(msft.high, 'MSFT_High')
        self.assertEqual(msft.low, 'MSFT_Low')
        self.assertEqual(msft.close, 'MSFT_Close')
        self.assertEqual(msft.volume, 'MSFT_Volume')
        self.assertEqual(msft.adj_close, 'MSFT_Adj Close')
        self.assertEqual(symbol_list.get('TEST'), None)
        self.assertEqual(goog.symbol, 'GOOG')
        self.assertEqual(goog.symbol, 'GOOG')
        self.assertEqual(goog.open, 'GOOG_Open')
        self.assertEqual(goog.high, 'GOOG_High')
        self.assertEqual(goog.low, 'GOOG_Low')
        self.assertEqual(goog.close, 'GOOG_Close')
        self.assertEqual(goog.volume, 'GOOG_Volume')
        self.assertEqual(goog.adj_close, 'GOOG_Adj Close')

if __name__ == "__main__":
    unittest.main()
