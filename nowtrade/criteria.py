"""
Module used to define strategy enter/exit criteria.
"""
import numpy as np
from nowtrade import logger
from nowtrade.action import Long, Short, LongExit, ShortExit
from nowtrade.technical_indicator import TechnicalIndicator

class Criteria(object):
    """
    All criteria must implement an apply(data_frame) function.
    All criteria must have a num_bars_required variable that corresponds
    to the number of bars it requires to provide a valid bool value.
    The apply function of all criteria must return a single boolean value.
    """
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)
        # Some TIs don't require the entire data_frame history.
        self.num_bars_required = None # Requires all history by default

class BarsSinceAction(Criteria):
    """
    Criteria for the number of bars that have passed since an particular
    action has occured.  Useful when strategies need to exit the market
    X bars after having entered.
    """
    def __init__(self, symbol, action, periods, condition=None):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.action = action.raw()
        self.periods = periods
        self.condition = str(condition).upper()
        self.num_bars_required = self.periods + 1
        self.label = 'BarsSinceAction_%s_%s_%s_%s' %(symbol, action, periods, condition)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'BarsSinceAction(symbol=%s, action=%s, periods=%s, condition=%s)' \
                %(self.symbol, self.action, self.periods, self.condition)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the BarsSinceAction criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if self.condition == 'OVER':
            values = data_frame['ACTIONS_%s' %self.symbol][-1-self.periods:].values
            return self.action not in values
        elif self.condition == 'UNDER':
            if self.periods < 1:
                return False
            values = data_frame['ACTIONS_%s' %self.symbol][-self.periods:].values
            return self.action in values
        else:
            if len(data_frame['ACTIONS_%s' %self.symbol]) >= self.num_bars_required:
                return self.action == data_frame['ACTIONS_%s' %self.symbol][-1-self.periods]
            return False

class BarsSinceLong(BarsSinceAction):
    """
    Same as BarsSinceAction, but specific to the Long action.
    """
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, Long(), periods, condition)
        self.label = 'BarsSinceLong_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceLong(symbol=%s, periods=%s, condition=%s)' \
                              %(self.symbol, self.periods, self.condition)
class BarsSinceShort(BarsSinceAction):
    """
    Same as BarsSinceAction, but specific to the Short action.
    """
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, Short(), periods, condition)
        self.label = 'BarsSinceShort_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceShort(symbol=%s, periods=%s, condition=%s)' \
                               %(self.symbol, self.periods, self.condition)
class BarsSinceLongExit(BarsSinceAction):
    """
    Same as BarsSinceAction, but specific to the LongExit action.
    """
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, LongExit(), periods, condition)
        self.label = 'BarsSinceLongExit_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceLongExit(symbol=%s, periods=%s, condition=%s)' \
                                  %(self.symbol, self.periods, self.condition)
class BarsSinceShortExit(BarsSinceAction):
    """
    Same as BarsSinceAction, but specific to the ShortExit action.
    """
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, ShortExit(), periods, condition)
        self.label = 'BarsSinceShortExit_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceShortExit(symbol=%s, periods=%s, condition=%s)' \
                                   %(self.symbol, self.periods, self.condition)

class InMarket(Criteria):
    """
    Criteria used to define if the strategy currently holds a position
    in the market with a specified symbol.
    """
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'InMarket_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'InMarket(symbol=%s)' %self.symbol
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the InMarket criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        try:
            return data_frame['STATUS_%s' %self.symbol][-1] != 0
        except KeyError:
            return False

class IsLong(Criteria):
    """
    Criteria used to define if the strategy currently holds a Long position
    in the market with a specified symbol.
    """
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'IsLong_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsLong(symbol=%s)' %self.symbol
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsLong criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        try:
            return data_frame['STATUS_%s' %self.symbol][-1] > 0
        except KeyError:
            return False

class IsShort(Criteria):
    """
    Criteria used to define if the strategy currently holds a Short position
    in the market with a specified symbol.
    """
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'IsShort_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsShort(symbol=%s)' %self.symbol
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsShort criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        try:
            return data_frame['STATUS_%s' %self.symbol][-1] < 0
        except KeyError:
            return False

class StopLoss(Criteria):
    """
    Criteria used to apply a stop loss exit rule to a strategy.

    Accepts an amount changed in pips/ticks or percent.
    """
    def __init__(self, symbol, value, short=False, percent=False):
        Criteria.__init__(self)
        self.symbol = symbol
        self.value = abs(value)
        self.short = short
        self.percent = percent
        self.label = 'StopLoss_%s_%s_%s_%s' %(symbol, value, short, percent)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'StopLoss(symbol=%s, value=%s, short=%s, percent=%s)' \
                %(self.symbol, self.value, self.short, self.percent)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the StopLoss criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if self.percent:
            check_value = data_frame['CHANGE_PERCENT_%s' %self.symbol][-1]
        else:
            check_value = data_frame['CHANGE_VALUE_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short:
                return check_value >= self.value
            else:
                return check_value <= -self.value
        return False

class TakeProfit(Criteria):
    """
    Criteria used to apply a take profit exit rule to a strategy.

    Only accept dollar amounts for now.
    """
    def __init__(self, symbol, value, short=False):
        Criteria.__init__(self)
        self.symbol = symbol
        self.value = value
        self.short = short
        self.label = 'TakeProfit_%s_%s_%s' %(symbol, value, short)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'TakeProfit(symbol=%s, value=%s, short=%s)' %(self.symbol, self.value, self.short)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the TakeProfit criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        check_value = data_frame['PL_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short:
                return check_value <= -self.value
            else:
                return check_value >= self.value
        return False

class TrailingStop(Criteria):
    """
    Criteria used to apply a trailing stop exit rule to a strategy.
    """
    def __init__(self, symbol, value, short=False, percent=False):
        Criteria.__init__(self)
        self.symbol = symbol
        self.value = value
        self.short = short
        self.percent = percent
        self.label = 'TrailingStop_%s_%s_%s_%s' %(symbol, value, short, percent)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'TrailingStop(symbol=%s, value=%s, short=%s, percent=%s)' \
                %(self.symbol, self.value, self.short, self.percent)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the TrailingStop criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if self.percent:
            check_value = data_frame['CHANGE_PERCENT_%s' %self.symbol][-1]
        else:
            check_value = data_frame['CHANGE_VALUE_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short:
                return self.value <= check_value
            else:
                return self.value >= check_value
        return False

class IsYear(Criteria):
    """
    Criteria to determine if the current strategy simulation is taking place
    on a specific year.
    """
    def __init__(self, year):
        """
        @type year: int
        """
        Criteria.__init__(self)
        self.year = year
        self.label = 'IsYear_%s' %self.year
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsYear(year=%s)' %(self.year)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsYear criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        return data_frame.index.year == self.year

class IsMonth(Criteria):
    """
    Criteria to determine if the current strategy simulation is taking place
    on a specific month.
    """
    def __init__(self, month):
        """
        @param month: 1 (January) to 12 (December)
        @type month: int
        """
        Criteria.__init__(self)
        self.month = month
        self.label = 'IsMonth_%s' %self.month
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsMonth(month=%s)' %(self.month)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsMonth criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        return data_frame.index.month == self.month

class IsDay(Criteria):
    """
    Criteria to determine if the current strategy simulation is taking place
    on a specific day.
    """
    def __init__(self, day):
        """
        @param day: 1-31
        @type day: int
        """
        Criteria.__init__(self)
        self.day = day
        self.label = 'IsDay_%s' %self.day
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsDay(day=%s)' %(self.day)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsDay criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        return data_frame.index.day == self.day

class IsWeekDay(Criteria):
    """
    Criteria to determine if the current strategy simulation is taking place
    on a specific weekday.
    """
    def __init__(self, weekday):
        """
        @param weekday: 0 (Monday) - 6 (Sunday)
        @type weekday: int
        """
        Criteria.__init__(self)
        self.weekday = weekday
        self.label = 'IsWeekDay_%s' %self.weekday
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsWeekDay(weekday=%s)' %(self.weekday)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the IsWeekDay criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        return data_frame.index.weekday == self.weekday
IsWeekday = IsWeekDay

class Above(Criteria):
    """
    Criteria used to determine if a technical indicator or symbol OHLCV is
    currently above another technical indicator, symbol OHLCV, or value.
    """
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        if isinstance(param1, TechnicalIndicator):
            param1 = param1.value
        if isinstance(param2, TechnicalIndicator):
            param2 = param2.value
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Above_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Above(param1=%s, param2=%s, lookback=%s)' %(self.param1, self.param2, self.lookback)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the Above criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if len(data_frame) < self.lookback:
            return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] > self.param2
        else:
            return data_frame[self.param1][-self.lookback] > data_frame[self.param2][-self.lookback]

class Below(Criteria):
    """
    Criteria used to determine if a technical indicator or symbol OHLCV is
    currently below another technical indicator, symbol OHLCV, or value.
    """
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        if isinstance(param1, TechnicalIndicator):
            param1 = param1.value
        if isinstance(param2, TechnicalIndicator):
            param2 = param2.value
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Below_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Below(param1=%s, param2=%s, lookback=%s)' %(self.param1, self.param2, self.lookback)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the Below criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if len(data_frame) < self.lookback:
            return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] < self.param2
        else:
            return data_frame[self.param1][-self.lookback] < data_frame[self.param2][-self.lookback]

class Equals(Criteria):
    """
    Criteria used to determine if a technical indicator or symbol OHLCV is
    currently equal to another technical indicator, symbol OHLCV, or value.
    """
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        if isinstance(param1, TechnicalIndicator):
            param1 = param1.value
        if isinstance(param2, TechnicalIndicator):
            param2 = param2.value
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Equals_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Equals(param1=%s, param2=%s, lookback=%s)' \
                %(self.param1, self.param2, self.lookback)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the Equal criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if len(data_frame) < self.lookback:
            return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] == self.param2
        else:
            return data_frame[self.param1][-self.lookback] == \
                   data_frame[self.param2][-self.lookback]
Equal = Equals

class InRange(Criteria):
    """
    Determines if a technical indicator or symbol OHLCV is in between
    two values. The two values can be other technical indicators, symbol
    OHLCV, or static values.
    """
    def __init__(self, ti, min_range, max_range):
        Criteria.__init__(self)
        if isinstance(ti, TechnicalIndicator):
            ti = ti.value
        self.technical_indicator = ti
        self.min_range = min_range
        self.max_range = max_range
        self.label = 'InRange_%s_%s_%s' %(ti, min_range, max_range)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'InRange(ti=%s, min_range=%s, max_range=%s)' \
                %(self.technical_indicator, self.min_range, self.max_range)
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the InRange criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        # Two number values to check
        if isinstance(self.min_range, (int, long, float)) and \
           isinstance(self.max_range, (int, long, float)):
            results = ((data_frame[self.technical_indicator] >= self.min_range) & \
                       (data_frame[self.technical_indicator] <= self.max_range))
        elif isinstance(self.min_range, (int, long, float)):
            results = ((data_frame[self.technical_indicator] >= self.min_range) & \
                       (data_frame[self.technical_indicator] <= data_frame[self.max_range]))
        elif isinstance(self.max_range, (int, long, float)):
            results = ((data_frame[self.technical_indicator] >= data_frame[self.min_range]) & \
                       (data_frame[self.technical_indicator] <= self.max_range))
        else:
            results = ((data_frame[self.technical_indicator] >= data_frame[self.min_range]) & \
                       (data_frame[self.technical_indicator] <= data_frame[self.max_range]))
        return results.iloc[-1]

class Not(Criteria):
    """
    Returns the inverses of another criteria's value.
    """
    def __init__(self, criteria):
        Criteria.__init__(self)
        self.criteria = criteria
        self.label = 'Not_%s' %criteria
        self.num_bars_required = criteria.num_bars_required
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Not(criteria=%s)' %self.criteria
    def __repr__(self):
        return self.label
    def apply(self, data_frame):
        """
        Apply the Not criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if self.criteria.apply(data_frame) == False:
            return True
        return False

class CrossingAbove(Criteria):
    """
    Criteria used to determine if a technical indicator or symbol OHLCV is
    in the process of crossing above another technical indicator, symbol
    OHLCV, or value.
    """
    def __init__(self, param1, param2):
        Criteria.__init__(self)
        if isinstance(param1, TechnicalIndicator):
            param1 = param1.value
        if isinstance(param2, TechnicalIndicator):
            param2 = param2.value
        self.param1 = param1
        self.param2 = param2
        self.num_bars_required = 2
        self.logger.info('Initialized - %s' %self)
    def __repr__(self):
        return 'CrossingAbove(param1=%s, param2=%s)' \
               %(self.param1, self.param2)
    def __str__(self):
        return 'CrossingAbove(param1=%s, param2=%s)' \
               %(self.param1, self.param2)
    def apply(self, data_frame):
        """
        Apply the CrossingAbove criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if len(data_frame) < self.num_bars_required:
            return False
        value1_now = data_frame[self.param1][-1]
        value1_previous = data_frame[self.param1][-2]
        if isinstance(self.param2, (int, long, float)):
            if value1_previous <= self.param2 and value1_now > self.param2:
                return True
        else:
            value2_now = data_frame[self.param2][-1]
            value2_previous = data_frame[self.param2][-2]
            if value1_previous <= value2_previous and value1_now > value2_now:
                return True
        return False

class CrossingBelow(Criteria):
    """
    Criteria used to determine if a technical indicator or symbol OHLCV is
    in the process of crossing below another technical indicator, symbol
    OHLCV, or value.
    """
    def __init__(self, param1, param2):
        Criteria.__init__(self)
        if isinstance(param1, TechnicalIndicator):
            param1 = param1.value
        if isinstance(param2, TechnicalIndicator):
            param2 = param2.value
        self.param1 = param1
        self.param2 = param2
        self.num_bars_required = 2
        self.logger.info('Initialized - %s' %self)
    def __repr__(self):
        return 'CrossingBelow(param1=%s, param2=%s)' \
               %(self.param1, self.param2)
    def __str__(self):
        return 'CrossingBelow(param1=%s, param2=%s)' \
               %(self.param1, self.param2)
    def apply(self, data_frame):
        """
        Apply the CrossingBelow criteria to the data_frame provided.
        @return Series(bool) The criteria status
        """
        if len(data_frame) < self.num_bars_required:
            return False
        value1_now = data_frame[self.param1][-1]
        value1_previous = data_frame[self.param1][-2]
        if isinstance(self.param2, (int, long, float)):
            if value1_previous >= self.param2 and value1_now < self.param2:
                return True
        else:
            value2_now = data_frame[self.param2][-1]
            value2_previous = data_frame[self.param2][-2]
            if value1_previous >= value2_previous and value1_now < value2_now:
                return True
        return False
