from nowtrade import logger
from nowtrade.report import Report

class TradingProfile:
    def __init__(self, capital, trading_amount, trading_fee, slippage=0.0):
        self.capital = capital
        self.trading_amount = trading_amount
        self.trading_fee = trading_fee
        self.slippage = slippage
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return 'TradingProfile(capital=%s, trading_amount=%s, trading_fee=%s, slippage=%s' %(self.capital, self.trading_amount, self.trading_fee, self.slippage)
    def __repr__(self): return 'TradingProfile(capital=%s, trading_amount=%s, trading_fee=%s, slippage=%s' %(self.capital, self.trading_amount, self.trading_fee, self.slippage)
