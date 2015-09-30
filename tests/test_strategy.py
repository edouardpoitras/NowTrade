import unittest
import datetime
import numpy as np
from testing_data import DummyDataConnection
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, report, strategy
from nowtrade.action import Long, Short, LongExit, ShortExit

class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.dc = DummyDataConnection()
        self.sl = symbol_list.SymbolList(['MSFT'])
        self.symbol = self.sl.get('msft')
        self.d = dataset.Dataset(self.sl, self.dc, None, None, 0)
        self.d.load_data()

    def test_simple_strategy(self):
        enter_crit = criteria.Above(self.symbol.close, 25.88)
        exit_crit = criteria.TimeSinceAction(self.symbol, Long(), 2)
        enter_crit_group = criteria_group.CriteriaGroup([enter_crit], Long(), self.symbol)
        exit_crit_group = criteria_group.CriteriaGroup([exit_crit], LongExit(), self.symbol)
        tp = trading_profile.TradingProfile(10000, trading_amount.StaticAmount(5000), trading_fee.StaticFee(0))
        strat = strategy.Strategy(self.d, [enter_crit_group, exit_crit_group], tp)
        strat.simulate()
        report_overview = strat.report.overview()
        self.assertEqual(strat.realtime_data_frame.iloc[2]['PL_MSFT'], report_overview['net_profit'])
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[0]['PL_PERCENT_MSFT']))
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[3]['PL_VALUE_MSFT']))
        self.assertEqual(strat.realtime_data_frame.iloc[0]['ACTIONS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['ACTIONS_MSFT'], -1)
        self.assertEqual(strat.realtime_data_frame.iloc[3]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[0]['STATUS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['STATUS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['STATUS_MSFT'], 0)
        self.assertEqual(report_overview['trades'], 1)
        self.assertEqual(report_overview['winning_trades'], 1)
        self.assertEqual(report_overview['losing_trades'], 0)
        self.assertEqual(report_overview['lacking_capital'], 0)
        self.assertEqual(report_overview['gross_profit'], report_overview['net_profit'])
        self.assertEqual(report_overview['ongoing_trades'], 0)
        self.assertEqual(report_overview['average_trading_amount'], 4996.7700000000004)
        self.assertEqual(report_overview['profitability'], 100.0)

    def test_stop_loss_strategy(self):
        enter_crit = criteria.Above(self.symbol.close, 25.88)
        exit_crit = criteria.StopLoss(self.symbol, -0.8)
        enter_crit_group = criteria_group.CriteriaGroup([enter_crit], Long(), self.symbol)
        exit_crit_group = criteria_group.CriteriaGroup([exit_crit], LongExit(), self.symbol)
        tp = trading_profile.TradingProfile(10000, trading_amount.StaticAmount(5000), trading_fee.StaticFee(0))
        strat = strategy.Strategy(self.d, [enter_crit_group, exit_crit_group], tp)
        strat.simulate()
        report_overview = strat.report.overview()
        self.assertEqual(strat.realtime_data_frame.iloc[-2]['PL_MSFT'], report_overview['net_profit'])
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[0]['PL_PERCENT_MSFT']))
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[-1]['PL_VALUE_MSFT']))
        self.assertEqual(strat.realtime_data_frame.iloc[0]['ACTIONS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[-2]['ACTIONS_MSFT'], -1)
        self.assertEqual(strat.realtime_data_frame.iloc[-1]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[0]['STATUS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['STATUS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[-2]['STATUS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[-1]['STATUS_MSFT'], 0)
        self.assertEqual(report_overview['trades'], 1)
        self.assertEqual(report_overview['winning_trades'], 0)
        self.assertEqual(report_overview['losing_trades'], 1)
        self.assertEqual(report_overview['lacking_capital'], 0)
        self.assertEqual(report_overview['gross_loss'], report_overview['net_profit'])
        self.assertEqual(report_overview['ongoing_trades'], 0)
        self.assertEqual(report_overview['average_trading_amount'], 4996.7700000000004)
        self.assertEqual(report_overview['profitability'], 0.0)

    def test_trailing_stop_long_strategy(self):
        enter_crit = criteria.Above(self.symbol.close, 25.88)
        exit_crit = criteria.TrailingStop(self.symbol, -0.2, short=True)
        enter_crit_group = criteria_group.CriteriaGroup([enter_crit], Long(), self.symbol)
        exit_crit_group = criteria_group.CriteriaGroup([exit_crit], LongExit(), self.symbol)
        tp = trading_profile.TradingProfile(10000, trading_amount.StaticAmount(5000), trading_fee.StaticFee(0))
        strat = strategy.Strategy(self.d, [enter_crit_group, exit_crit_group], tp)
        strat.simulate()
        report_overview = strat.report.overview()
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[0]['PL_PERCENT_MSFT']))
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[-5]['PL_VALUE_MSFT']))
        self.assertEqual(strat.realtime_data_frame.iloc[1]['PL_VALUE_MSFT'], 0.57000000000000028)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['PL_MSFT'], 187.20999999999913)
        self.assertEqual(strat.realtime_data_frame.iloc[0]['ACTIONS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['ACTIONS_MSFT'], -1)
        self.assertEqual(strat.realtime_data_frame.iloc[3]['ACTIONS_MSFT'], 0)

    def test_trailing_stop_short_strategy(self):
        enter_crit = criteria.Above(self.symbol.close, 25.88)
        exit_crit = criteria.TrailingStop(self.symbol, -0.2)
        enter_crit_group = criteria_group.CriteriaGroup([enter_crit], Long(), self.symbol)
        exit_crit_group = criteria_group.CriteriaGroup([exit_crit], LongExit(), self.symbol)
        tp = trading_profile.TradingProfile(10000, trading_amount.StaticAmount(5000), trading_fee.StaticFee(0))
        strat = strategy.Strategy(self.d, [enter_crit_group, exit_crit_group], tp)
        strat.simulate()
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[0]['PL_PERCENT_MSFT']))
        self.assertTrue(np.isnan(strat.realtime_data_frame.iloc[-4]['PL_VALUE_MSFT']))
        self.assertEqual(strat.realtime_data_frame.iloc[1]['PL_VALUE_MSFT'], 0.57000000000000028)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['PL_MSFT'], 187.20999999999913)
        self.assertEqual(strat.realtime_data_frame.iloc[3]['PL_PERCENT_MSFT'], -0.003862495171881071)
        self.assertEqual(strat.realtime_data_frame.iloc[0]['ACTIONS_MSFT'], 1)
        self.assertEqual(strat.realtime_data_frame.iloc[1]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[2]['ACTIONS_MSFT'], 0)
        self.assertEqual(strat.realtime_data_frame.iloc[3]['ACTIONS_MSFT'], -1)
        self.assertEqual(strat.realtime_data_frame.iloc[4]['ACTIONS_MSFT'], 0)

"""
Too lazy to re-create these strategies with static data.

class TestSlingshotStrategy(unittest.TestCase):
    def test_slingshot_strategy(self):
        dc = data_connection.MongoDatabaseConnection(database='symbol-data-1min-currency')
        sl = symbol_list.SymbolList(['EURUSD'])
        eurusd = sl.get('EURUSD')
        start = datetime.datetime(2013, 01, 01)
        end = datetime.datetime(2014, 01, 01)
        d = dataset.Dataset(sl, dc, start, end, 0)
        d.load_data()
        d.resample('5min', False)
        sma = technical_indicator.SMA(eurusd.close, 21)
        d.add_technical_indicator(sma)
        stoch = technical_indicator.STOCH(eurusd, 21, 10, 0, 4, 0)
        d.add_technical_indicator(stoch)
        stochf = technical_indicator.STOCHF(eurusd, 5, 2, 0)
        d.add_technical_indicator(stochf)
        stochf_previous = technical_indicator.Shift(stochf.fastk, 1)
        d.add_technical_indicator(stochf_previous)
        columns = [stochf.fastk, stoch.slowk]
        columns = [eurusd.close, sma.value]
        # Enter Long
        enter_crit_long1 = criteria.Above(stoch.slowk, 80)
        enter_crit_long2 = criteria.Below(stochf_previous.value, 20)
        enter_crit_long3 = criteria.Above(stochf.fastk, 20)
        enter_crit_long4 = criteria.Below(sma.value, eurusd.low)
        # Enter Short
        enter_crit_short1 = criteria.Below(stoch.slowk, 20)
        enter_crit_short2 = criteria.Above(stochf_previous.value, 80)
        enter_crit_short3 = criteria.Below(stochf.fastk, 80)
        enter_crit_short4 = criteria.Above(sma.value, eurusd.high)
        # Exit Long
        #exit_crit_long1 = criteria.TrailingStop(eurusd, 0.0030)
        exit_crit_long1 = criteria.Below(stoch.slowk, 20)
        exit_crit_long2 = criteria.Above(stochf_previous.value, 80)
        exit_crit_long3 = criteria.Below(stochf.fastk, 80)
        exit_crit_long4 = criteria.Above(sma.value, eurusd.high)
        # Exit Short
        #exit_crit_short1 = criteria.TrailingStop(eurusd, 0.0030, short=True)
        exit_crit_short1 = criteria.Above(stoch.slowk, 80)
        exit_crit_short2 = criteria.Below(stochf_previous.value, 20)
        exit_crit_short3 = criteria.Above(stochf.fastk, 20)
        exit_crit_short4 = criteria.Below(sma.value, eurusd.low)
        # Criteria Groups
        enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long1, enter_crit_long2, enter_crit_long3, enter_crit_long4], LongExit(), eurusd)
        enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short1, enter_crit_short2, enter_crit_short3, enter_crit_short4], ShortExit(), eurusd)
        #exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long1], LongExit(), eurusd)
        #exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short1], ShortExit(), eurusd)
        exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long1, exit_crit_long2, exit_crit_long3, exit_crit_long4], Long(), eurusd)
        exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short1, exit_crit_short2, exit_crit_short3, exit_crit_short4], Short(), eurusd)
        # Strategy
        tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(0))
        strat = strategy.Strategy(d, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2], tp)
        strat.simulate()
        print strat.report.overview()
"""

if __name__ == "__main__":
    unittest.main()
