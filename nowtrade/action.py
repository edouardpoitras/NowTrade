"""
The actions module contains classes representing all the different actions
that can be taken in the markets.
"""
from nowtrade import logger

LONG = 1
SHORT = 2
NO_ACTION = 0
LONG_EXIT = -1
SHORT_EXIT = -2

ACTIONS_MAP = {1: 'LONG',
               2: 'SHORT',
               0: 'NO_ACTION',
               -1: 'LONG_EXIT',
               -2: 'SHORT_EXIT'}

class Action(object):
    """
    Abstract Action object represents an action to be taken in the market.
    """
    def __init__(self, name):
        self.name = name.replace(' ', '').replace('_', '').replace('-', '').lower()
        self.logger = logger.Logger(self.__class__.__name__)
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        other = str(other).replace(' ', '').replace('_', '').replace('-', '').lower()
        return other == self.name
    def raw(self):
        """
        A raw (int) representation of the action.
        """
        return NO_ACTION

class Long(Action):
    """
    Long Action represents going long in the market.
    """
    def __init__(self):
        Action.__init__(self, 'long')
    def raw(self):
        """
        A raw (int) representation of the action.
        """
        return LONG

class LongExit(Action):
    """
    Long Exit Action represents exiting a long position from the market.
    """
    def __init__(self):
        Action.__init__(self, 'longexit')
    def __eq__(self, other):
        other = str(other).replace(' ', '').replace('_', '').replace('-', '').lower()
        return other == 'longexit' or other == 'exitlong'
    def raw(self):
        """
        A raw (int) representation of the action.
        """
        return LONG_EXIT

class ExitLong(LongExit):
    """
    Alias to LongExit().
    """
    pass

class Short(Action):
    """
    Short Action represents shorting in the market.
    """
    def __init__(self):
        Action.__init__(self, 'short')
    def raw(self):
        """
        A raw (int) representation of the action.
        """
        return SHORT

class ShortExit(Action):
    """
    Short Exit Action represents exiting a short position from the market.
    """
    def __init__(self):
        Action.__init__(self, 'shortexit')
    def __eq__(self, other):
        other = str(other).replace(' ', '').replace('_', '').replace('-', '').lower()
        return other == 'shortexit' or other == 'exitshort'
    def raw(self):
        """
        A raw (int) representation of the action.
        """
        return SHORT_EXIT

class ExitShort(ShortExit):
    """
    Alias to ShortExit().
    """
    pass
