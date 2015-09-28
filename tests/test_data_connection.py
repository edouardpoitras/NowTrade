import datetime
import unittest
from nowtrade.data_connection import YahooConnection, \
                            GoogleConnection, \
                            ForexiteConnection, \
                            MongoDatabaseConnection
from testing_data import msft_data

"""
Tests should not be accessing external resources.
Commenting out all the DataConnection tests for now.

class TestYahooConnection(unittest.TestCase):
    def test_get_data(self):
        yc = YahooConnection()
        data = yc.get_data('MSFT',
                           datetime.datetime(2010, 06, 01),
                           datetime.datetime(2010, 06, 10))
        self.assertEqual(float('%.2f' %data['MSFT_Open'].sum()), 205.66)
        self.assertEqual(float('%.2f' %data['MSFT_High'].sum()), 208.05)
        self.assertEqual(float('%.2f' %data['MSFT_Low'].sum()), 202.7)
        self.assertEqual(float('%.2f' %data['MSFT_Close'].sum()), 205.19)
        self.assertEqual(float('%.2f' %data['MSFT_Volume'].sum()), 634076500)
        sanity = msft_data[['MSFT_Open', 'MSFT_High', 'MSFT_Low', 'MSFT_Close', 'MSFT_Volume']] == data[['MSFT_Open', 'MSFT_High', 'MSFT_Low', 'MSFT_Close', 'MSFT_Volume']]
        self.assertTrue(sanity.all().all())

class TestGoogleConnection(unittest.TestCase):
    def test_get_data(self):
        gc = GoogleConnection()
        data = gc.get_data('MSFT',
                           datetime.datetime(2010, 06, 01),
                           datetime.datetime(2010, 06, 10))
        self.assertEqual(float('%.2f' %data['MSFT_Open'].sum()), 205.66)
        self.assertEqual(float('%.2f' %data['MSFT_High'].sum()), 208.05)
        self.assertEqual(float('%.2f' %data['MSFT_Low'].sum()), 202.7)
        self.assertEqual(float('%.2f' %data['MSFT_Close'].sum()), 205.19)
        self.assertEqual(float('%.2f' %data['MSFT_Volume'].sum()), 634116786)

    def test_get_tick(self):
        gc = GoogleConnection()
        data = gc.get_ticks('MSFT', period='1d')
        column_sanity = data.columns == [u'MSFT_Close', u'MSFT_High', u'MSFT_Low', u'MSFT_Open', u'MSFT_Volume']
        self.assertTrue(column_sanity.all())

class TestMongoConnection(unittest.TestCase):
    def setUp(self):
        self.mc = MongoDatabaseConnection(database='test-mongo-connection')
        self.symbol = 'MSFT'

    def test_set_data(self):
        self.mc.set_data(msft_data, [self.symbol])
        data = self.mc.get_data(self.symbol, datetime.datetime(2010, 06, 01), datetime.datetime(2010, 06, 10))
        data = data[[u'MSFT_Open', u'MSFT_High', u'MSFT_Low', u'MSFT_Close', u'MSFT_Volume', u'MSFT_Adj Close']]
        sanity = msft_data[['MSFT_Open', 'MSFT_High', 'MSFT_Low', 'MSFT_Close', 'MSFT_Volume', 'MSFT_Adj Close']] == data
        self.assertTrue(sanity.all().all())

    def tearDown(self):
        self.mc.connection.drop_database(self.mc.database)
"""

if __name__ == "__main__":
    unittest.main()
