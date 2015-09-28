from nowtrade import logger

class TradingFee(object):
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)

class StaticFee(TradingFee):
    def __init__(self, fee):
        TradingFee.__init__(self)
        self.fee = fee
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return 'StaticFee(fee=%s)' %self.fee
    def __repr__(self): return 'StaticFee(fee=%s)' %self.fee
    def get_fee(self, price, shares): return self.fee
