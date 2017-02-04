"""
This module is used as a way of managing and accessing the different symbols
being used in a strategy.
"""
from nowtrade import logger

class SymbolList(object):
    """
    Holds a list of symbol objects and makes it easy for the user to
    retrieve them by name.
    """
    def __init__(self, symbols):
        self.symbols = [Symbol(symbol) for symbol in symbols]
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info(symbols)
    def get(self, symbol):
        """
        Returns the symbol object named after the symbol parameter.
        """
        symbol = symbol.upper()
        for sym in self.symbols:
            if symbol == sym.symbol:
                return sym
        self.logger.error('Could not find symbol: %s' %symbol)
        return None
    def __repr__(self):
        return str(self.symbols)
    def __str__(self):
        return str(self.symbols)
    def __iter__(self):
        return iter(self.symbols)
StockList = SymbolList

class Symbol(object):
    """
    A symbol object allows for easily accessing a symbol's various attributes
    such as the OHLCV and Adj.C of a symbol.
    """
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.open = '%s_Open' %self.symbol
        self.high = '%s_High' %self.symbol
        self.low = '%s_Low' %self.symbol
        self.close = '%s_Close' %self.symbol
        self.volume = '%s_Volume' %self.symbol
        self.adj_close = '%s_Adj Close' %self.symbol
    def __repr__(self):
        return str(self.symbol)
    def __str__(self):
        return str(self.symbol)
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, other):
        return self.symbol == other
    def custom(self, name):
        """
        Used for custom columns pulled from a DB.
        """
        return '%s_%s' %(self.symbol, name)
