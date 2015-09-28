from nowtrade import logger

class Trade:
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
        return str([self.datetime, self.action, self.symbol, self.price, self.shares, self.money, self.fee, self.slippage])
    def __repr__(self): return self.__str__()
