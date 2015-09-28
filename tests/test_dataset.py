import unittest
from nowtrade import symbol_list, dataset, technical_indicator
from testing_data import DummyDataConnection, msft_data

class TestDataset(unittest.TestCase):
    def setUp(self):
        self.dc = DummyDataConnection()
        self.sl = symbol_list.SymbolList(['msft'])
        self.symbol = self.sl.get('msft')

    def test_dataset(self):
        d = dataset.Dataset(self.sl, self.dc, None, None, 0)
        d.load_data()
        sanity = msft_data[['MSFT_Open', 'MSFT_High', 'MSFT_Low', 'MSFT_Close', 'MSFT_Volume', 'MSFT_Adj Close']] == d.data_frame[[u'MSFT_Open', u'MSFT_High', u'MSFT_Low', u'MSFT_Close', u'MSFT_Volume', u'MSFT_Adj Close']]
        self.assertTrue(sanity.all().all())
        addition = technical_indicator.Addition(self.symbol.close, 1)
        d.add_technical_indicator(addition)
        self.assertIn(addition.value, d.data_frame.columns)
        self.assertEqual(len(d.data_frame[addition.value]), len(msft_data))
        self.assertEqual(len(d.technical_indicators), 1)
        self.assertEqual(d.technical_indicators[0], addition)

if __name__ == "__main__":
    unittest.main()
