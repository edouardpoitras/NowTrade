"""
Trading fee module contains all the different types of trading fee classes
that can be applied to a trading profile.
"""
from nowtrade import logger

class TradingFee(object):
    """
    The base class for all trading fee classes.
    Simply initializes the logger for now.
    """
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)

class StaticFee(TradingFee):
    """
    The StaticFee simply applies the same static fee to all entry/exit trades.
    """
    def __init__(self, fee):
        TradingFee.__init__(self)
        self.fee = fee
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'StaticFee(fee=%s)' %self.fee
    def __repr__(self):
        return 'StaticFee(fee=%s)' %self.fee
    def get_fee(self, price, shares): # pylint: disable=unused-argument
        """
        Given a symbol price and the amount of shares purchased, this method
        will return the fees incurred for the trade.
        """
        return self.fee
