import unittest
from nowtrade.symbol_list import SymbolList

class TestSymbolList(unittest.TestCase):
    def test_symbol_list(self):
        sanity = ['MSFT', 'GOOG', 'AAPL']
        symbols = ['msft', 'gOOg', 'AAPl']
        symbol_list = SymbolList(symbols)
        for symbol in symbol_list: sanity.remove(str(symbol))
        self.assertEqual(len(sanity), 0)
        msft = symbol_list.get('msft')
        self.assertEqual(msft.symbol, 'MSFT')
        self.assertEqual(msft.symbol, 'MSFT')
        self.assertEqual(msft.open, 'MSFT_Open')
        self.assertEqual(msft.high, 'MSFT_High')
        self.assertEqual(msft.low, 'MSFT_Low')
        self.assertEqual(msft.close, 'MSFT_Close')
        self.assertEqual(msft.volume, 'MSFT_Volume')
        self.assertEqual(msft.adj_close, 'MSFT_Adj Close')

if __name__ == "__main__":
    unittest.main()
