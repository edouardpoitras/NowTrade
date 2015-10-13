"""
Module holding various classes the define the rules for how many shares to
purchase on every market entry.
"""
from math import ceil
from nowtrade import logger

class TradingAmount(object):
    """
    The base class for all trading amount objects.
    """
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)

class StaticAmount(TradingAmount):
    """
    A TradingAmount that always returns the number of shares to most closely
    approximate a certain amount in dollars to be put in a trade.
    """
    def __init__(self, amount, round_up=False):
        TradingAmount.__init__(self)
        self.amount = amount
        self.round_up = round_up
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'StaticAmount(amount=%s, round_up=%s)' %(self.amount, self.round_up)
    def __repr__(self):
        return 'StaticAmount(amount=%s, round_up=%s)' %(self.amount, self.round_up)
    def get_shares(self, price, available_money): # pylint: disable=unused-argument
        """
        Return the number of shares to purchase based on the current symbol
        price and the amount of capital available to your trading profile.
        """
        if self.round_up:
            shares = ceil(self.amount / price)
        else:
            shares = round(self.amount / price)
        return shares

class NumberOfShares(TradingAmount):
    """
    A TradingAmount that always returns the same number of shares to be traded.
    """
    def __init__(self, shares):
        TradingAmount.__init__(self)
        self.shares = shares
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'NumberOfShares(shares=%s)' %self.shares
    def __repr__(self):
        return 'NumberOfShares(shares=%s)' %self.shares
    def get_shares(self, price, available_money): # pylint: disable=unused-argument
        """
        Return the number of shares to purchase based on the current symbol
        price and the amount of capital available to your trading profile.
        """
        return self.shares

class CapitalPercentage(TradingAmount):
    """
    A TradingAmount that always returns the number of shares equivalent to
    your trading profile's capital percentage specified.
    """
    def __init__(self, percent):
        TradingAmount.__init__(self)
        self.percent = percent
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'CapitalPercentage(percent=%s)' %self.percent
    def __repr__(self):
        return 'CapitalPercentage(percent=%s)' %self.percent
    def get_shares(self, price, available_money):
        """
        Return the number of shares to purchase based on the current symbol
        price and the amount of capital available to your trading profile.
        """
        return round(self.percent * available_money / price / 100)

class KellyCriterion(TradingAmount):
    """
    K% = W - [(1 - 2) / R]
    W is Winning Probability (# Winning Trades / Total Trades)
    R is Win/Loss Ratio (Avg. Gains / Avg. Losses)
    @todo: Incomplete... finish and test this implementation
    """
    def __init__(self, win_probability, average_gains, average_losses):
        print 'WARNING: The KellyCriterion object is incomplete'
        TradingAmount.__init__(self)
        self.win_probability = win_probability
        self.average_gains = average_gains
        self.average_losses = average_losses
        self.ratio = average_gains / average_losses
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'KellyCriterion(win_probability=%s, average_gains=%s, average_losses=%s)' \
                             %(self.win_probability, self.average_gains, self.average_losses)
    def __repr__(self):
        return 'KellyCriterion(win_probability=%s, average_gains=%s, average_losses=%s)' \
                             %(self.win_probability, self.average_gains, self.average_losses)
    def get_shares(self, price, available_money): # pylint: disable=unused-argument
        """
        Return the number of shares to purchase based on the current symbol
        price and the amount of capital available to your trading profile.
        """
        k = self.win_probability - ((1 - self.win_probability) / self.ratio)
        return available_money * k
