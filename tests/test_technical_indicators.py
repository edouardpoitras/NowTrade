import unittest
import numpy as np
import pandas as pd
from nowtrade import technical_indicator
from nowtrade.neural_network import NeuralNetwork
from nowtrade.ensemble import Ensemble
from testing_data import msft_data, msft_close_name

class NeuralNetworkMockObject(NeuralNetwork):
    def __init__(self, train_data, prediction_data):
        NeuralNetwork.__init__(self, train_data, prediction_data)
    def activate_all(self, data_frame):
        return [1, 2, 3, 4, 5, 6, 7, 8];

class EnsembleMockObject(Ensemble):
    def __init__(self, train_data, prediction_data):
        Ensemble.__init__(self, train_data, prediction_data)
    def activate_all(self, data_frame):
        return [1, 2, 3, 4, 5, 6, 7, 8];

class TestTechnicalIndicator(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame([[0, 5, 10.0], [5, 4, 12.0], [10, 3, 8.0], [15, 2, 6.0], [20, 1, 9.0], [25, 0, 10.0]], columns=['one', 'two', 'three'])

class TestAddition(TestTechnicalIndicator):
    def test_addition(self):
        data = msft_data.copy()
        ti = technical_indicator.Addition(msft_close_name, 1)
        ti.results(data)
        sanity = data['ADDITION_MSFT_Close_1'] == data[msft_close_name] + 1
        self.assertTrue(sanity.all())
        data['TEST'] = data[msft_close_name] + 1
        ti2 = technical_indicator.Addition(msft_close_name, 'TEST')
        ti2.results(data)
        sanity = data['ADDITION_MSFT_Close_1'] == data['TEST']
        self.assertTrue(sanity.all())

class TestSubtraction(TestTechnicalIndicator):
    def test_subtraction(self):
        data = msft_data.copy()
        ti = technical_indicator.Subtraction(msft_close_name, 1)
        ti.results(data)
        sanity = data['SUBTRACTION_MSFT_Close_1'] == data[msft_close_name] - 1
        self.assertTrue(sanity.all())
        data['TEST'] = data[msft_close_name] - 1
        ti2 = technical_indicator.Subtraction(msft_close_name, 'TEST')
        ti2.results(data)
        sanity = data['SUBTRACTION_MSFT_Close_1'] == data['TEST']
        self.assertTrue(sanity.all())

class TestMultiplication(TestTechnicalIndicator):
    def test_multiplication(self):
        data = msft_data.copy()
        ti = technical_indicator.Multiplication(msft_close_name, 2)
        ti.results(data)
        sanity = data['MULTIPLICATION_MSFT_Close_2'] == data[msft_close_name] * 2
        self.assertTrue(sanity.all())
        data['TEST'] = data[msft_close_name] * 2
        ti2 = technical_indicator.Multiplication(msft_close_name, 'TEST')
        ti2.results(data)
        sanity = data['MULTIPLICATION_MSFT_Close_2'] == data['TEST']
        self.assertTrue(sanity.all())

class TestDivision(TestTechnicalIndicator):
    def test_division(self):
        data = msft_data.copy()
        ti = technical_indicator.Division(msft_close_name, 2)
        ti.results(data)
        sanity = data['DIVISION_MSFT_Close_2'] == data[msft_close_name] / 2
        self.assertTrue(sanity.all())
        data['TEST'] = data[msft_close_name] / 2
        ti2 = technical_indicator.Division(msft_close_name, 'TEST')
        ti2.results(data)
        sanity = data['DIVISION_MSFT_Close_2'] == data['TEST']
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

class TestATR(TestTechnicalIndicator):
    def test_atr(self):
        data = msft_data.copy()
        ti = technical_indicator.ATR('MSFT', 3)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][2]))
        self.assertAlmostEqual(data[ti.value][3], 0.83666666)
        self.assertAlmostEqual(data[ti.value][4], 0.75444444)
        self.assertAlmostEqual(data[ti.value][5], 0.71629629)

class TestBBANDS(TestTechnicalIndicator):
    def test_bbands(self):
        data = msft_data.copy()
        ti = technical_indicator.BBANDS('MSFT_Close', 2)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.upper][5]))
        self.assertTrue(np.isnan(data[ti.value][5]))
        self.assertTrue(np.isnan(data[ti.middle][5]))
        self.assertTrue(np.isnan(data[ti.lower][5]))
        self.assertAlmostEqual(data[ti.upper][6], 25.2425772)
        self.assertAlmostEqual(data[ti.value][6], 24.9225772)
        self.assertAlmostEqual(data[ti.middle][6], 24.9225772)
        self.assertAlmostEqual(data[ti.lower][6], 24.6025772)
        self.assertAlmostEqual(data[ti.upper][7], 25.11451697)
        self.assertAlmostEqual(data[ti.value][7], 24.90451697)
        self.assertAlmostEqual(data[ti.middle][7], 24.90451697)
        self.assertAlmostEqual(data[ti.lower][7], 24.69451697)

class TestDX(TestTechnicalIndicator):
    def test_dx(self):
        data = msft_data.copy()
        ti = technical_indicator.DX('MSFT', 3)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][2]))
        self.assertAlmostEqual(data[ti.value][3], 31.30193905)
        self.assertAlmostEqual(data[ti.value][4], 53.38345864)
        self.assertAlmostEqual(data[ti.value][5], 73.34049986)

class TestADX(TestTechnicalIndicator):
    def test_adx(self):
        data = msft_data.copy()
        ti = technical_indicator.ADX('MSFT', 3)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][4]))
        self.assertTrue(np.isnan(data[ti.plus_di][2]))
        self.assertTrue(np.isnan(data[ti.minus_di][2]))
        self.assertAlmostEqual(data[ti.value][5], 52.67529919)
        self.assertAlmostEqual(data[ti.plus_di][3], 19.80830670)
        self.assertAlmostEqual(data[ti.minus_di][3], 37.85942492)

class TestULTOSC(TestTechnicalIndicator):
    def test_ultosc(self):
        data = msft_data.copy()
        ti = technical_indicator.ULTOSC('MSFT', 1, 2, 3)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][2]))
        self.assertAlmostEqual(data[ti.value][3], 25.58258795)
        self.assertAlmostEqual(data[ti.value][4], 12.35037988)

class TestSTOCH(TestTechnicalIndicator):
    def test_stoch(self):
        data = msft_data.copy()
        ti = technical_indicator.STOCH('MSFT', fast_k_period=3, slow_k_period=2, slow_d_period=2)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][3]))
        self.assertTrue(np.isnan(data[ti.slowk][3]))
        self.assertTrue(np.isnan(data[ti.slowd][3]))
        self.assertAlmostEqual(data[ti.value][4], 7.96783955)
        self.assertAlmostEqual(data[ti.slowk][4], 7.96783955)
        self.assertAlmostEqual(data[ti.slowd][4], 30.9870598)
        self.assertAlmostEqual(data[ti.value][5], 13.4584566)
        self.assertAlmostEqual(data[ti.slowk][5], 13.4584566)
        self.assertAlmostEqual(data[ti.slowd][5], 10.71314808)

class TestSTOCHF(TestTechnicalIndicator):
    def test_stochf(self):
        data = msft_data.copy()
        ti = technical_indicator.STOCHF('MSFT', fast_k_period=3, fast_d_period=2)
        ti.results(data)
        self.assertTrue(np.isnan(data[ti.value][2]))
        self.assertTrue(np.isnan(data[ti.fastk][2]))
        self.assertTrue(np.isnan(data[ti.fastd][2]))
        self.assertAlmostEqual(data[ti.value][3], 12.97709923)
        self.assertAlmostEqual(data[ti.fastk][3], 12.97709923)
        self.assertAlmostEqual(data[ti.fastd][3], 54.00628011)
        self.assertAlmostEqual(data[ti.value][4], 2.95857988)
        self.assertAlmostEqual(data[ti.fastk][4], 2.95857988)
        self.assertAlmostEqual(data[ti.fastd][4], 7.96783955)

class TestNeuralNetwork(TestTechnicalIndicator):
    def test_neural_network(self):
        data = msft_data.copy()
        network = NeuralNetworkMockObject(data, data)
        ti = technical_indicator.NeuralNetwork(network, 'NNTest')
        ti.results(data)
        self.assertEqual(data['NEURAL_NETWORK_NNTest'][0], 1)
        self.assertEqual(data['NEURAL_NETWORK_NNTest'][1], 2)
        self.assertEqual(data['NEURAL_NETWORK_NNTest'][2], 3)

class TestEnsemble(TestTechnicalIndicator):
    def test_ensemble(self):
        data = msft_data.copy()
        ensemble = EnsembleMockObject(data, data)
        ti = technical_indicator.Ensemble(ensemble, 'EnsembleTest')
        ti.results(data)
        self.assertEqual(data['ENSEMBLE_EnsembleTest'][0], 1)
        self.assertEqual(data['ENSEMBLE_EnsembleTest'][1], 2)
        self.assertEqual(data['ENSEMBLE_EnsembleTest'][2], 3)

if __name__ == "__main__":
    unittest.main()
