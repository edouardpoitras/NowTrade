from math import ceil
from nowtrade import logger

class TradingAmount(object):
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)

class StaticAmount(TradingAmount):
    def __init__(self, amount, round_up=False):
        TradingAmount.__init__(self)
        self.amount = amount
        self.round_up = round_up
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return 'StaticAmount(amount=%s, round_up=%s)' %(self.amount, self.round_up)
    def __repr__(self): return 'StaticAmount(amount=%s, round_up=%s)' %(self.amount, self.round_up)
    def get_shares(self, price, available_money):
        if self.round_up: shares = ceil(self.amount / price)
        else: shares = round(self.amount / price)
        return shares

class NumberOfShares(TradingAmount):
    def __init__(self, shares):
        TradingAmount.__init__(self)
        self.shares = shares
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return 'NumberOfShares(shares=%s)' %self.shares
    def __repr__(self): return 'NumberOfShares(shares=%s)' %self.shares
    def get_shares(self, price, capital): return self.shares

class CapitalPercentage(TradingAmount):
    def __init__(self, percent):
        TradingAmount.__init__(self)
        self.percent = percent
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return 'CapitalPercentage(percent=%s)' %self.percent
    def __repr__(self): return 'CapitalPercentage(percent=%s)' %self.percent
    def get_shares(self, price, available_money):
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
        self.w = win_probability
        self.r = average_gains / average_losses
        self.logger.info('Initialized - %s' %self)
    def get_shares(self, price, available_money):
        k = self.w - ((1 - self.w) / self.r)
        return capital * k
