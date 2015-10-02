import numpy as np
import pandas as pd
from nowtrade import logger
from nowtrade import action

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
        return 'BarsSinceAction(symbol=%s, action=%s, periods=%s, condition=%s)' %(self.symbol, self.action, self.periods, self.condition)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if self.condition == 'OVER':
            values = data_frame['ACTIONS_%s' %self.symbol][-1-self.periods:].values
            return self.action not in values
        elif self.condition == 'UNDER':
            if self.periods < 1: return False
            values = data_frame['ACTIONS_%s' %self.symbol][-self.periods:].values
            return self.action in values
        else:
            if len(data_frame['ACTIONS_%s' %self.symbol]) >= self.num_bars_required:
                return self.action == data_frame['ACTIONS_%s' %self.symbol][-1-self.periods]
            return False

class BarsSinceLong(BarsSinceAction):
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, action.Long(), periods, condition)
        self.label = 'BarsSinceLong_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceLong(symbol=%s, periods=%s, condition=%s)' %(self.symbol, self.periods, self.condition)
class BarsSinceShort(BarsSinceAction):
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, action.Short(), periods, condition)
        self.label = 'BarsSinceShort_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceShort(symbol=%s, periods=%s, condition=%s)' %(self.symbol, self.periods, self.condition)
class BarsSinceLongExit(BarsSinceAction):
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, action.LongExit(), periods, condition)
        self.label = 'BarsSinceLongExit_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceLongExit(symbol=%s, periods=%s, condition=%s)' %(self.symbol, self.periods, self.condition)
class BarsSinceShortExit(BarsSinceAction):
    def __init__(self, symbol, periods, condition=None):
        BarsSinceAction.__init__(self, symbol, action.ShortExit(), periods, condition)
        self.label = 'BarsSinceShortExit_%s_%s_%s' %(symbol, periods, condition)
    def __str__(self):
        return 'BarsSinceShortExit(symbol=%s, periods=%s, condition=%s)' %(self.symbol, self.periods, self.condition)

class InMarket(Criteria):
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'InMarket_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'InMarket(symbol=%s)' %self.symbol
    def __repr__(self): return self.label
    def apply(self, data_frame):
        try: return data_frame['STATUS_%s' %self.symbol][-1] != 0
        except: return False

class IsLong(Criteria):
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'IsLong_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsLong(symbol=%s)' %self.symbol
    def __repr__(self): return self.label
    def apply(self, data_frame):
        try: return data_frame['STATUS_%s' %self.symbol][-1] > 0
        except: return False

class IsShort(Criteria):
    def __init__(self, symbol):
        Criteria.__init__(self)
        self.symbol = str(symbol)
        self.label = 'IsShort_%s' %symbol
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'IsShort(symbol=%s)' %self.symbol
    def __repr__(self): return self.label
    def apply(self, data_frame):
        try: return data_frame['STATUS_%s' %self.symbol][-1] < 0
        except: return False

class StopLoss(Criteria):
    """ Accepts an amount changed in pips/ticks or percent """
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
        return 'StopLoss(symbol=%s, value=%s, short=%s, percent=%s)' %(self.symbol, self.value, self.short, self.percent)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if self.percent: check_value = data_frame['PL_PERCENT_%s' %self.symbol][-1]
        else: check_value = data_frame['PL_VALUE_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short: return check_value >= self.value
            else: return check_value <= -self.value
        return False

class TakeProfit(Criteria):
    """ Only accept dollar amounts for now"""
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
    def __repr__(self): return self.label
    def apply(self, data_frame):
        check_value = data_frame['PL_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short: return check_value <= -self.value
            else: return check_value >= self.value
        return False

class TrailingStop(Criteria):
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
        return 'TrailingStop(symbol=%s, value=%s, short=%s, percent=%s)' %(self.symbol, self.value, self.short, self.percent)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if self.percent: check_value = data_frame['PL_PERCENT_%s' %self.symbol][-1]
        else: check_value = data_frame['PL_VALUE_%s' %self.symbol][-1]
        if not np.isnan(check_value):
            if self.short: return self.value <= check_value
            else: return self.value >= check_value
        return False

class IsYear(Criteria):
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
    def __repr__(self): return self.label
    def apply(self, data_frame):
        return data_frame.index.year == self.year

class IsMonth(Criteria):
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
    def __repr__(self): return self.label
    def apply(self, data_frame):
        return data_frame.index.month == self.month

class IsDay(Criteria):
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
    def __repr__(self): return self.label
    def apply(self, data_frame):
        return data_frame.index.day == self.day

class IsWeekDay(Criteria):
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
    def __repr__(self): return self.label
    def apply(self, data_frame):
        return data_frame.index.weekday == self.weekday

class Position(Criteria):
    def __init__(self, param1, position, param2):
        Criteria.__init__(self)
        self.param1 = param1 # Technical indicator label
        self.position = position.upper() # ABOVE or BELOW
        self.param2 = param2 # Technical indicator label or int or long or float
        self.label = 'Position_%s_%s_%s' %(param1, position, param2)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Position(param1=%s, position=%s, param2=%s)' %(self.param1, self.position, self.param2)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        results = pd.Series(False, index=data_frame.index)
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            if self.position == 'ABOVE':
                results = data_frame[self.param1] > self.param2
            elif self.position == 'BELOW':
                results = data_frame[self.param1] < self.param2
            else: results = data_frame[self.param1] == self.param2
        else: # Compare two technical indicators
            if self.position == 'ABOVE':
                results = data_frame[self.param1] > data_frame[self.param2]
            elif self.position == 'BELOW':
                results = data_frame[self.param1] < data_frame[self.param2]
            else: results = data_frame[self.param1] == data_frame[self.param2]
        return results.iloc[-1]

class Above(Criteria):
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Above_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Above(param1=%s, param2=%s, lookback=%s)' %(self.param1, self.param2, self.lookback)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if len(data_frame) < self.lookback: return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] > self.param2
        else: return data_frame[self.param1][-self.lookback] > data_frame[self.param2][-self.lookback]

class Below(Criteria):
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Below_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Below(param1=%s, param2=%s, lookback=%s)' %(self.param1, self.param2, self.lookback)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if len(data_frame) < self.lookback: return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] < self.param2
        else: return data_frame[self.param1][-self.lookback] < data_frame[self.param2][-self.lookback]

class Equals(Criteria):
    def __init__(self, param1, param2, lookback=1):
        Criteria.__init__(self)
        self.param1 = param1 # Technical indicator label
        self.param2 = param2 # Technical indicator label or int or long or float
        self.lookback = lookback
        self.label = 'Equals_%s_%s_%s' %(param1, param2, lookback)
        self.num_bars_required = lookback
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Equals(param1=%s, param2=%s, lookback=%s)' %(self.param1, self.param2, self.lookback)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if len(data_frame) < self.lookback: return False
        # Second value is not a technical indicator, simply a number to compare
        if isinstance(self.param2, (int, long, float)):
            return data_frame[self.param1][-self.lookback] == self.param2
        else: return data_frame[self.param1][-self.lookback] == data_frame[self.param2][-self.lookback]
Equal = Equals

class InRange(Criteria):
    """
    Determines if a technical indicator is in between two values.
    The two values can be other technical indicators.
    """
    def __init__(self, ti, min_range, max_range):
        Criteria.__init__(self)
        self.ti = ti
        self.min_range = min_range
        self.max_range = max_range
        self.label = 'InRange_%s_%s_%s' %(ti, min_range, max_range)
        self.num_bars_required = 1
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'InRange(ti=%s, min_range=%s, max_range=%s)' %(self.ti, self.min_range, self.max_range)
    def __repr__(self): return self.label
    def apply(self, data_frame):
        # Two number values to check
        if isinstance(self.min_range, (int, long, float)) and isinstance(self.max_range, (int, long, float)):
            results = ((data_frame[self.ti] >= self.min_range) & (data_frame[self.ti] <= self.max_range))
        elif isinstance(self.min_range, (int, long, float)):
            results = ((data_frame[self.ti] >= self.min_range) & (data_frame[self.ti] <= data_frame[self.max_range]))
        elif isinstance(self.max_range, (int, long, float)):
            results = ((data_frame[self.ti] >= data_frame[self.min_range]) & (data_frame[self.ti] <= self.max_range))
        else:
            results = ((data_frame[self.ti] >= data_frame[self.min_range]) & (data_frame[self.ti] <= data_frame[self.max_range]))
        return results.iloc[-1]

class Not(Criteria):
    """
    Checks for the inverses of a criteria is true.
    """
    def __init__(self, criteria):
        Criteria.__init__(self)
        self.criteria = criteria
        self.label = 'Not_%s' %criteria
        self.num_bars_required = criteria.num_bars_required
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Not(criteria=%s)' %self.criteria
    def __repr__(self): return self.label
    def apply(self, data_frame):
        if self.criteria.apply(data_frame) == False: return True
        return False

class Crossing(Criteria):
    def __init__(self, param1, direction, param2):
        Criteria.__init__(self)
        self.direction = direction.lower()
        self.param1 = param1
        self.param2 = param2
        self.num_bars_required = 2
        self.logger.info('Initialized - %s' %self)
    def __repr__(self):
        return 'Crossing(param1=%s, direction=%s, param2=%s)' \
               %(self.param1, self.direction, self.param2)
    def __str__(self):
        return 'Crossing(param1=%s, direction=%s, param2=%s)' \
               %(self.param1, self.direction, self.param2)
    def apply(self, data_frame):
        if len(data_frame) < self.num_bars_required: return False
        value1_now = data_frame[self.param1][-1]
        value1_previous = data_frame[self.param1][-2]
        if isinstance(self.param2, (int, long, float)):
            if self.direction == 'above' and value1_previous <= self.param2 and value1_now > self.param2: return True
            elif self.direction == 'below' and value1_previous >= self.param2 and value1_now < self.param2: return True
        else:
            value2_now = data_frame[self.param2][-1]
            value2_previous = data_frame[self.param2][-2]
            if self.direction == 'above' and value1_previous <= value2_previous and value1_now > value2_now: return True
            elif self.direction == 'below' and value1_previous >= value2_previous and value1_now < value2_now: return True
        return False
