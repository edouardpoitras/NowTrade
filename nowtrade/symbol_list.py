from nowtrade import logger

class SymbolList(object):
    def __init__(self, symbols):
        self.symbols = [Symbol(symbol) for symbol in symbols]
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info(symbols)
    def get(self, symbol):
        symbol = symbol.upper()
        for s in self.symbols:
            if symbol == s.symbol: return s
        return None
    def __repr__(self): return str(self.symbols)
    def __str__(self): return str(self.symbols)
    def __iter__(self):
        return iter(self.symbols)
class StockList(SymbolList):
    def __init__(self, symbols):
        SymbolList.__init__(self, symbols)

class Symbol(object):
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.symbol = self.symbol
        self.open = '%s_Open' %self.symbol
        self.high = '%s_High' %self.symbol
        self.low = '%s_Low' %self.symbol
        self.close = '%s_Close' %self.symbol
        self.volume = '%s_Volume' %self.symbol
        self.adj_close = '%s_Adj Close' %self.symbol
    def __repr__(self): return str(self.symbol)
    def __str__(self): return str(self.symbol)
    def __hash__(self): return hash(self.symbol)
    def __eq__(self, other): return self.symbol == other
