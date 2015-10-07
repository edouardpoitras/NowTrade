"""
Criteria group module associates various criteria with corresponding actions.
"""
from nowtrade.criteria import InMarket, IsLong, IsShort, Not
from nowtrade.action import Long, LongExit, Short, ShortExit, \
                            LONG, LONG_EXIT, SHORT, SHORT_EXIT, NO_ACTION
from nowtrade import logger

class InvalidAction(Exception):
    """
    Exception raised when an invalid action is submitted to a criteria group.
    """
    pass

class CriteriaGroup(object):
    """
    For now, since we haven't implemented adding to positions,
    the default is InMarket, NotInMarket, IsLong, IsShort gets
    added automatically to criteria groups as needed.
    """
    def __init__(self, criteria_list, action, symbol):
        self.criteria_list = criteria_list
        self.action = action
        self._action = 0
        self.symbol = str(symbol)
        # Add Actions Criteria Automatically
        if self.action == Long():
            self.criteria_list.append(Not(InMarket(self.symbol)))
            self._action = LONG
        elif self.action == LongExit():
            self.criteria_list.append(IsLong(self.symbol))
            self._action = LONG_EXIT
        elif self.action == Short():
            self.criteria_list.append(Not(InMarket(self.symbol)))
            self._action = SHORT
        elif self.action == ShortExit():
            self.criteria_list.append(IsShort(self.symbol))
            self._action = SHORT_EXIT
        else: raise InvalidAction()
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('New Criteria Group - %s for %s (%s)' \
                         %(str(action).upper(), symbol, criteria_list))

    def __str__(self):
        return 'CriteriaGroup(criteria_list=%s, action=%s, symbol=%s)' \
                              %(self.criteria_list, self.action, self.symbol)
    def __repr__(self):
        return 'CriteriaGroup(criteria_list=%s, action=%s, symbol=%s)' \
                              %(self.criteria_list, self.action, self.symbol)

    def get_result(self, data_frame):
        """
        Get the results of this criteria group based on the data_frame
        provided. If all criteria are True, return the action.
        """
        results = []
        for criteria in self.criteria_list:
            result = None
            if criteria.num_bars_required is not None:
                result = criteria.apply(data_frame[-criteria.num_bars_required:])
            else: result = criteria.apply(data_frame)
            results.append(result)
            self.logger.debug('Criteria - %s: %s' %(criteria, result))
        if False in results:
            return NO_ACTION
        else: return self._action
