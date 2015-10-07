"""
The trade module contains the Trade class which is a container class for
a trade having been performed in the market.
"""
from nowtrade import logger

class Trade(object):
    """
    Trade object has access to a trade's datetime, action, symbol, price,
    shares, money, fee, and slippage.
    """
    def __init__(self, datetime, action, symbol, price, shares, money, fee, slippage):
        self.datetime = datetime
        self.action = action
        self.symbol = symbol
        self.price = price
        self.shares = shares
        self.money = money
        self.fee = fee
        self.slippage = slippage
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('Initialized - %s' %self)

    def __str__(self):
        return 'Trade(datetime=%s, action=%s, symbol=%s, price=%s, shares=%s, \
money=%s, fee=%s, slippage=%s)' \
                %(self.datetime, self.action, self.symbol, self.price, \
                  self.shares, self.money, self.fee, self.slippage)
    def __repr__(self):
        return 'Trade(' + str([self.datetime, self.action, self.symbol, \
                               self.price, self.shares, self.money, self.fee, self.slippage]) + ')'
