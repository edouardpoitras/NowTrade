import unittest
import numpy as np
import pandas as pd
from nowtrade import technical_indicator
from testing_data import msft_data, msft_close_name

class TestTechnicalIndicator(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame([[0, 5, 10.0], [5, 4, 12.0], [10, 3, 8.0], [15, 2, 6.0], [20, 1, 9.0], [25, 0, 10.0]], columns=['one', 'two', 'three'])

class TestAddition(TestTechnicalIndicator):
    def test_addition(self):
        ti = technical_indicator.Addition(msft_close_name, 1)
        ti.results(msft_data)
        sanity = msft_data['ADDITION_MSFT_Close_1'] == msft_data[msft_close_name] + 1
        self.assertTrue(sanity.all())
        msft_data['TEST'] = msft_data[msft_close_name] + 1
        ti2 = technical_indicator.Addition(msft_close_name, 'TEST')
        ti2.results(msft_data)
        sanity = msft_data['ADDITION_MSFT_Close_1'] == msft_data['TEST']
        self.assertTrue(sanity.all())

class TestSubtraction(TestTechnicalIndicator):
    def test_subtraction(self):
        ti = technical_indicator.Subtraction(msft_close_name, 1)
        ti.results(msft_data)
        sanity = msft_data['SUBTRACTION_MSFT_Close_1'] == msft_data[msft_close_name] - 1
        self.assertTrue(sanity.all())
        msft_data['TEST'] = msft_data[msft_close_name] - 1
        ti2 = technical_indicator.Subtraction(msft_close_name, 'TEST')
        ti2.results(msft_data)
        sanity = msft_data['SUBTRACTION_MSFT_Close_1'] == msft_data['TEST']
        self.assertTrue(sanity.all())

class TestMultiplication(TestTechnicalIndicator):
    def test_multiplication(self):
        ti = technical_indicator.Multiplication(msft_close_name, 2)
        ti.results(msft_data)
        sanity = msft_data['MULTIPLICATION_MSFT_Close_2'] == msft_data[msft_close_name] * 2
        self.assertTrue(sanity.all())
        msft_data['TEST'] = msft_data[msft_close_name] * 2
        ti2 = technical_indicator.Multiplication(msft_close_name, 'TEST')
        ti2.results(msft_data)
        sanity = msft_data['MULTIPLICATION_MSFT_Close_2'] == msft_data['TEST']
        self.assertTrue(sanity.all())

class TestDivision(TestTechnicalIndicator):
    def test_division(self):
        ti = technical_indicator.Division(msft_close_name, 2)
        ti.results(msft_data)
        sanity = msft_data['DIVISION_MSFT_Close_2'] == msft_data[msft_close_name] / 2
        self.assertTrue(sanity.all())
        msft_data['TEST'] = msft_data[msft_close_name] / 2
        ti2 = technical_indicator.Division(msft_close_name, 'TEST')
        ti2.results(msft_data)
        sanity = msft_data['DIVISION_MSFT_Close_2'] == msft_data['TEST']
        self.assertTrue(sanity.all())

class TestPercentChange(TestTechnicalIndicator):
    def test_percent_change(self):
        ti1 = technical_indicator.PercentChange('one', 'two')
        ti1.results(self.data)
        self.assertEqual(self.data['PERCENT_CHANGE_one_two'][0], np.inf)
        self.assertEqual(self.data['PERCENT_CHANGE_one_two'][1], -0.2)
        self.assertEqual(self.data['PERCENT_CHANGE_one_two'][2], -0.7)
        ti2 = technical_indicator.PercentChange('one', 1)
        ti2.results(self.data)
        self.assertEqual(self.data['PERCENT_CHANGE_one_1'][1], np.inf)
        self.assertEqual(self.data['PERCENT_CHANGE_one_1'][2], 1)
        self.assertEqual(self.data['PERCENT_CHANGE_one_1'][3], 0.5)

class TestMax(TestTechnicalIndicator):
    def test_max(self):
        ti = technical_indicator.Max('three', 2)
        ti.results(self.data)
        self.assertEqual(self.data['MAX_three_2'][2], 12)
        ti = technical_indicator.Max('three', 4)
        ti.results(self.data)
        self.assertEqual(self.data['MAX_three_4'][4], 12)
        self.assertEqual(self.data['MAX_three_4'][5], 10)

class TestMin(TestTechnicalIndicator):
    def test_min(self):
        ti = technical_indicator.Min('three', 2)
        ti.results(self.data)
        self.assertEqual(self.data['MIN_three_2'][4], 6)
        ti = technical_indicator.Max('three', 4)
        ti.results(self.data)
        self.assertEqual(self.data['MAX_three_4'][5], 10)

class TestShift(TestTechnicalIndicator):
    def test_shift(self):
        ti1 = technical_indicator.Shift('one', 2)
        ti1.results(self.data)
        self.assertEqual(self.data['one'][1], self.data['SHIFT_one_2'][3])

class TestSMA(TestTechnicalIndicator):
    def test_sma(self):
        ti1 = technical_indicator.SMA('one', 2)
        ti1.results(self.data)
        self.assertEqual(self.data['one'][0], 0)
        self.assertEqual(self.data['one'][1], 5)
        self.assertEqual(self.data['one'][2], 10)
        self.assertEqual(self.data['one'][3], 15)
        self.assertEqual(self.data['SMA_one_2'][1], 2.5)
        self.assertEqual(self.data['SMA_one_2'][3], 12.5)

class TestEMA(TestTechnicalIndicator):
    def test_ema(self):
        ti = technical_indicator.EMA('three', 3)
        ti.results(self.data)
        sanity = self.data['three'] == pd.Series([10.0, 12.0, 8.0, 6.0, 9.0, 10.0])
        self.assertTrue(sanity.all())
        self.assertEqual(self.data['EMA_three_3'][2], 10.0)
        self.assertEqual(self.data['EMA_three_3'][3], 8.0)
        self.assertEqual(self.data['EMA_three_3'][4], 8.5)
        self.assertEqual(self.data['EMA_three_3'][5], 9.25)

class TestRSI(TestTechnicalIndicator):
    def test_rsi(self):
        ti = technical_indicator.RSI('three', 3)
        ti.results(self.data)
        sanity = self.data['three'] == pd.Series([10.0, 12.0, 8.0, 6.0, 9.0, 10.0])
        self.assertTrue(sanity.all())
        self.assertEqual(self.data['RSI_three_3'][3], 25.0)
        self.assertEqual(self.data['RSI_three_3'][4], 52.0)

if __name__ == "__main__":
    unittest.main()
