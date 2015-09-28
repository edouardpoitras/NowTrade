import unittest
import pandas as pd
from nowtrade import criteria
from testing_data import msft_data, msft_close_name
from nowtrade.symbol_list import Symbol
from nowtrade.action import Long, Short, LongExit, ShortExit
from nowtrade.strategy import LONG, SHORT, LONG_EXIT, SHORT_EXIT, NO_ACTION

class TestCriteria(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame([[0, 5, 10.0, NO_ACTION, 0, 10, -0.10, 0.01],
                                  [5, 4, 12.0, LONG, 1, 20, -0.20, 0.02],
                                  [10, 3, 8.0, NO_ACTION, 1, 30, -0.30, 0.01],
                                  [15, 2, 6.0, LONG_EXIT, 0, 0, -0.20, 0.00],
                                  [20, 1, 9.0, NO_ACTION, 0, -10, -0.10, -0.01],
                                  [25, 0, 10.0, SHORT, -1, -20, 0.0, -0.02],
                                  [30, -1, 11.0, SHORT_EXIT, 0, 0, 0.10, -0.03]],
                                 columns=['ONE', 'TWO', 'THREE', 'ACTIONS_ONE', 'STATUS_ONE', 'PL_ONE', 'PL_VALUE_ONE', 'PL_PERCENT_ONE'],
                                 index=pd.date_range('20100601', periods=7))
        self.one = Symbol('ONE')
        self.two = Symbol('TWO')
        self.three = Symbol('THREE')

class TestTimeSinceAction(TestCriteria):
    def test_time_since_action(self):
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 2)
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 1)
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 0)
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 4)
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 5)
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 6)
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 0, 'under')
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 1, 'under')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 2, 'under')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 5, 'under')
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 6, 'under')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 7, 'under')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 1, 'over')
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, ShortExit(), 0, 'over')
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Short(), 0, 'over')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 4, 'over')
        self.assertTrue(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 5, 'over')
        self.assertFalse(crit.apply(self.data))
        crit = criteria.TimeSinceAction(self.one, Long(), 6, 'over')
        self.assertFalse(crit.apply(self.data))

class TestInMarket(TestCriteria):
    def test_in_market(self):
        crit = criteria.InMarket(self.one)
        self.assertTrue(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-1]))
        self.assertFalse(crit.apply(self.data[:2]))
        self.assertTrue(crit.apply(self.data[:3]))

class TestIsLong(TestCriteria):
    def test_is_long(self):
        crit = criteria.IsLong(self.one)
        self.assertFalse(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-1]))
        self.assertTrue(crit.apply(self.data[:3]))

class TestIsShort(TestCriteria):
    def test_is_short(self):
        crit = criteria.IsShort(self.one)
        self.assertTrue(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-1]))
        self.assertFalse(crit.apply(self.data[:2]))

class TestIsYear(TestCriteria):
    def test_is_year(self):
        crit = criteria.IsYear(2012)
        self.assertFalse(crit.apply(self.data).any())
        crit = criteria.IsYear(2010)
        self.assertTrue(crit.apply(self.data).all())

class TestIsMonth(TestCriteria):
    def test_is_month(self):
        crit = criteria.IsMonth(6)
        self.assertTrue(crit.apply(self.data).all())
        crit = criteria.IsMonth(1)
        self.assertFalse(crit.apply(self.data).any())

class TestIsDay(TestCriteria):
    def test_is_day(self):
        crit = criteria.IsDay(7)
        self.assertTrue(crit.apply(self.data)[-1])
        crit = criteria.IsDay(8)
        self.assertFalse(crit.apply(self.data)[-1])

class TestIsWeekDay(TestCriteria):
    def test_is_week_day(self):
        crit = criteria.IsWeekDay(0)
        self.assertTrue(crit.apply(self.data)[-1])
        crit = criteria.IsWeekDay(4)
        self.assertTrue(crit.apply(self.data)[-4])
        crit = criteria.IsWeekDay(3)
        self.assertFalse(crit.apply(self.data)[-1])

class TestPosition(TestCriteria):
    def test_position(self):
        crit = criteria.Position('ONE', 'above', 5)
        value = crit.apply(self.data.head(2))
        self.assertEqual(value, False)
        value = crit.apply(self.data.head(3))
        self.assertEqual(value, True)
        crit = criteria.Position('ONE', 'below', 5)
        value = crit.apply(self.data.head(1))
        self.assertEqual(value, True)
        value = crit.apply(self.data.head(2))
        self.assertEqual(value, False)
        value = crit.apply(self.data.head(3))
        self.assertEqual(value, False)
        crit = criteria.Position('ONE', 'above', 'TWO')
        value = crit.apply(self.data.head(1))
        self.assertEqual(value, False)
        value = crit.apply(self.data.head(2))
        self.assertEqual(value, True)
        crit = criteria.Position('ONE', 'below', 'TWO')
        value = crit.apply(self.data.head(1))
        self.assertEqual(value, True)
        value = crit.apply(self.data.head(2))
        self.assertEqual(value, False)
        crit = criteria.Position('ONE', 'equal', 10)
        value = crit.apply(self.data.head(2))
        self.assertEqual(value, False)
        value = crit.apply(self.data.head(3))
        self.assertEqual(value, True)
        value = crit.apply(self.data.head(4))
        self.assertEqual(value, False)

class TestInRange(TestCriteria):
    def test_in_range(self):
        crit = criteria.InRange(str(self.one), 10, 20)
        ret = crit.apply(self.data.head(2))
        self.assertFalse(ret)
        ret = crit.apply(self.data.head(3))
        self.assertTrue(ret)
        ret = crit.apply(self.data.head(4))
        self.assertTrue(ret)
        ret = crit.apply(self.data.head(5))
        self.assertTrue(ret)
        ret = crit.apply(self.data.head(6))
        self.assertFalse(ret)
        crit = criteria.InRange(str(self.one), str(self.two), str(self.three))
        ret = crit.apply(self.data.head(1))
        self.assertFalse(ret)
        ret = crit.apply(self.data.head(2))
        self.assertTrue(ret)
        ret = crit.apply(self.data.head(3))
        self.assertFalse(ret)

class TestCrossing(TestCriteria):
    def test_crossing(self):
        crit = criteria.Crossing(str(self.one), 'above', str(self.two))
        self.assertTrue(crit.apply(self.data.head(2)))
        crit = criteria.Crossing(str(self.one), 'below', str(self.two))
        self.assertFalse(crit.apply(self.data.head(2)))
        crit = criteria.Crossing(str(self.three), 'below', str(self.one))
        self.assertFalse(crit.apply(self.data.head(2)))
        self.assertTrue(crit.apply(self.data.head(3)))
        crit = criteria.Crossing(str(self.two), 'below', 2)
        self.assertFalse(crit.apply(self.data.head(4)))
        self.assertTrue(crit.apply(self.data.head(5)))

class TestNot(TestCriteria):
    def test_not(self):
        inRangeCriteria = criteria.InRange(str(self.one), 10, 20)
        crit = criteria.Not(inRangeCriteria)
        ret = crit.apply(self.data.head(2))
        self.assertTrue(ret)
        ret = crit.apply(self.data.head(3))
        self.assertFalse(ret)
        ret = crit.apply(self.data.head(4))
        self.assertFalse(ret)
        ret = crit.apply(self.data.head(5))
        self.assertFalse(ret)
        ret = crit.apply(self.data.head(6))
        self.assertTrue(ret)

class TestStopLoss(TestCriteria):
    def test_stop_loss(self):
        crit = criteria.StopLoss(self.one, -0.2)
        self.assertFalse(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-2]))
        self.assertTrue(crit.apply(self.data[:-3]))
        crit = criteria.StopLoss(self.one, -0.02, percent=True)
        self.assertTrue(crit.apply(self.data))
        self.assertTrue(crit.apply(self.data[:-1]))
        self.assertFalse(crit.apply(self.data[:-2]))
        crit = criteria.StopLoss(self.one, -0.1, short=True)
        self.assertTrue(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-1]))
        crit = criteria.StopLoss(self.one, -0.02, short=True, percent=True)
        self.assertFalse(crit.apply(self.data))
        self.assertFalse(crit.apply(self.data[:-1]))
        self.assertTrue(crit.apply(self.data[:2]))

class TestTakeProfit(TestCriteria):
    def test_take_profit(self):
        crit = criteria.TakeProfit(self.one, 20)
        self.assertTrue(crit.apply(self.data[:2]))
        self.assertFalse(crit.apply(self.data[:-1]))

if __name__ == "__main__":
    unittest.main()
