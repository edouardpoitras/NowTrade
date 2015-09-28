import pandas as pd
import numpy as np
import talib
import uuid
from nowtrade import logger

class TechnicalIndicator(object):
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)

class Pair(TechnicalIndicator):
    """
    Pair is a helper TI created to aid in pairs trading.
    Attributes:
        ols -> Ordinary Least Squares of the pair
        hedge_ratio -> The pair's hedge ratio
        spread -> The spread between the pair
        zscore -> The zscore between the pair
    """
    def __init__(self, y_data, x_data, lookback):
        TechnicalIndicator.__init__(self)
        self.y_data = y_data
        self.x_data = x_data
        self.lookback = lookback
        self.value = 'PAIR_%s_%s_%s' %(y_data, x_data, lookback)
        self.ols = self.value
        self.hedge_ratio = 'HEDGE_RATIO_%s_%s_%s' %(y_data, x_data, lookback)
        self.spread = 'SPREAD_%s_%s_%s' %(y_data, x_data, lookback)
        self.zscore = 'ZSCORE_%s_%s_%s' %(y_data, x_data, lookback)
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return self.value
    def __repr__(self): return self.value
    def results(self, data_frame):
        y = data_frame[self.y_data]
        x = data_frame[self.x_data]
        if self.lookback >= len(x):
            return ([self.value, self.hedge_ratio, self.spread, self.zscore], \
                    [pd.Series(np.nan), pd.Series(np.nan), pd.Series(np.nan), pd.Series(np.nan)])
        ols_result = pd.ols(y=y, x=x, window=self.lookback)
        hedge_ratio = ols_result.beta['x']
        spread = y - hedge_ratio * x
        data_frame[self.value] = ols_result.resid
        data_frame[self.hedge_ratio] = hedge_ratio
        data_frame[self.spread] = spread
        data_frame[self.zscore] = (spread - pd.rolling_mean(spread, self.lookback)) / pd.rolling_std(spread, self.lookback)

class Addition(TechnicalIndicator):
    def __init__(self, data1, data2):
        TechnicalIndicator.__init__(self)
        self.data1 = data1
        self.data2 = data2
        self.value = 'ADDITION_%s_%s' %(data1, data2)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Addition(data1=%s, data2=%s)' %(self.data1, self.data2)
    def __repr__(self): return self.value
    def results(self, data_frame):
        if isinstance(self.data2, basestring): # Other TI
            data_frame[self.value] = data_frame[self.data1] + data_frame[self.data2]
        else:
            data_frame[self.value] = data_frame[self.data1] + self.data2

class Subtraction(TechnicalIndicator):
    def __init__(self, data1, data2):
        TechnicalIndicator.__init__(self)
        self.data1 = data1
        self.data2 = data2
        self.value = 'SUBTRACTION_%s_%s' %(data1, data2)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Subtraction(data1=%s, data2=%s)' %(self.data1, self.data2)
    def __repr__(self): return self.value
    def results(self, data_frame):
        if isinstance(self.data2, basestring): # Other TI
            data_frame[self.value] = data_frame[self.data1] - data_frame[self.data2]
        else:
            data_frame[self.value] = data_frame[self.data1] - self.data2

class Multiplication(TechnicalIndicator):
    def __init__(self, data1, data2):
        TechnicalIndicator.__init__(self)
        self.data1 = data1
        self.data2 = data2
        self.value = 'MULTIPLICATION_%s_%s' %(data1, data2)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Multiplication(data1=%s, data2=%s)' %(self.data1, self.data2)
    def __repr__(self): return self.value
    def results(self, data_frame):
        if isinstance(self.data2, basestring): # Other TI
            data_frame[self.value] = data_frame[self.data1] * data_frame[self.data2]
        else:
            data_frame[self.value] = data_frame[self.data1] * self.data2

class Division(TechnicalIndicator):
    def __init__(self, data1, data2):
        TechnicalIndicator.__init__(self)
        self.data1 = data1
        self.data2 = data2
        self.value = 'DIVISION_%s_%s' %(data1, data2)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Division(data1=%s, data2=%s)' %(self.data1, self.data2)
    def __repr__(self): return self.value
    def results(self, data_frame):
        if isinstance(self.data2, basestring): # Other TI
            data_frame[self.value] = data_frame[self.data1] / data_frame[self.data2]
        else:
            data_frame[self.value] = data_frame[self.data1] / self.data2

class PercentChange(TechnicalIndicator):
    def __init__(self, data1, data2):
        TechnicalIndicator.__init__(self)
        self.data1 = data1
        self.data2 = data2
        self.value = 'PERCENT_CHANGE_%s_%s' %(data1, data2)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'PercentChange(data1=%s, data2=%s)' %(self.data1, self.data2)
    def __repr__(self): return self.value
    def results(self, data_frame):
        if isinstance(self.data2, basestring): # Other TI
            series1 = data_frame[self.data1]
            series2 = data_frame[self.data2]
            data_frame[self.value] = (series2 - series1) / series1
        else: # Value
            data_frame[self.value] = data_frame[self.data1].pct_change(self.data2)

class Max(TechnicalIndicator):
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.value = 'MAX_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Max(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try: data_frame[self.value] = pd.rolling_max(data_frame[self.data], self.period)
        except: data_frame[self.value] = np.nan

class Min(TechnicalIndicator):
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.value = 'MIN_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Min(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try: data_frame[self.value] = pd.rolling_min(data_frame[self.data], self.period)
        except: data_frame[self.value] = np.nan

class InvalidShift(Exception): pass
class Shift(TechnicalIndicator):
    """
    A period of 2 will retrieve values back in time.
    IE: From [1, 2, 3, 4] to [Nan, Nan, 1, 2]
    """
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        if period < 1: raise InvalidShift('Must be positive shift period')
        self.data = data
        self.period = period
        self.value = 'SHIFT_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'Shift(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        data_frame[self.value] = data_frame[self.data].shift(self.period)

class SMA(TechnicalIndicator):
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.value = 'SMA_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'SMA(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        data_frame[self.value] = pd.rolling_mean(data_frame[self.data], self.period)

class EMA(TechnicalIndicator):
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.value = 'EMA_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'EMA(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try: data_frame[self.value] = talib.EMA(data_frame[self.data].values, self.period)
        except: data_frame[self.value] = np.nan

class RSI(TechnicalIndicator):
    def __init__(self, data, period):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.value = 'RSI_%s_%s' %(data, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'RSI(data=%s, period=%s)' %(self.data, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try: data_frame[self.value] = talib.RSI(data_frame[self.data].values, timeperiod=self.period)
        except: data_frame[self.value] = np.nan

class ATR(TechnicalIndicator):
    def __init__(self, symbol, period):
        TechnicalIndicator.__init__(self)
        self.symbol = symbol
        self.period = period
        self.value = 'ATR_%s_%s' %(symbol, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'ATR(symbol=%s, period=%s)' %(self.symbol, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try: data_frame[self.value] = talib.ATR(data_frame['%s_High' %self.symbol].values,
                        data_frame['%s_Low' %self.symbol].values,
                        data_frame['%s_Close' %self.symbol].values,
                        timeperiod=self.period)
        except: data_frame[self.value] = np.nan

class BBANDS(TechnicalIndicator):
    def __init__(self, data, period, devup=2, devdown=2, ma_type=talib.MA_Type.T3):
        TechnicalIndicator.__init__(self)
        self.data = data
        self.period = period
        self.devup = 2
        self.devdown = 2
        self.ma_type = ma_type
        self.value = 'BBANDS_MIDDLE_%s_%s_%s_%s_%s' %(data, period, devup, devdown, ma_type)
        self.upper = 'BBANDS_UPPER_%s_%s_%s_%s_%s' %(data, period, devup, devdown, ma_type)
        self.middle = self.value
        self.lower = 'BBANDS_LOWER_%s_%s_%s_%s_%s' %(data, period, devup, devdown, ma_type)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'BBANDS(data=%s, period=%s, devup=%s, devdown=%s, ma_type=%s)' %(self.data, self.period, self.devup, self.devdown, self.ma_type)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            upper, middle, lower = talib.BBANDS(data_frame[self.data].values, self.period, self.devup, self.devdown, matype=self.ma_type)
            data_frame[self.upper] = upper
            data_frame[self.middle] = middle
            data_frame[self.lower] = lower
        except:
            data_frame[self.middle] = np.nan
            data_frame[self.lower] = np.nan
            data_frame[self.lower] = np.nan

class DX(TechnicalIndicator):
    def __init__(self, symbol, period):
        TechnicalIndicator.__init__(self)
        self.symbol = symbol
        self.period = period
        self.value = 'DX_%s_%s' %(symbol, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'DX(symbol=%s, period=%s)' %(self.symbol, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            dx = talib.DX(data_frame['%s_High' %self.symbol].values,
                          data_frame['%s_Low' %self.symbol].values,
                          data_frame['%s_Close' %self.symbol].values,
                          timeperiod=self.period)
            data_frame[self.value] = dx
        except:
            data_frame[self.value] = np.nan

class ADX(TechnicalIndicator):
    def __init__(self, symbol, period):
        TechnicalIndicator.__init__(self)
        self.symbol = symbol
        self.period = period
        self.value = 'ADX_%s_%s' %(symbol, period)
        self.plus_di = '+DI_%s_%s' %(symbol, period)
        self.minus_di = '-DI_%s_%s' %(symbol, period)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'ADX(symbol=%s, period=%s)' %(self.symbol, self.period)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            adx = talib.ADX(data_frame['%s_High' %self.symbol].values,
                            data_frame['%s_Low' %self.symbol].values,
                            data_frame['%s_Close' %self.symbol].values,
                            timeperiod=self.period)
            plus_di = talib.PLUS_DI(data_frame['%s_High' %self.symbol].values,
                                    data_frame['%s_Low' %self.symbol].values,
                                    data_frame['%s_Close' %self.symbol].values,
                                    timeperiod=self.period)
            minus_di = talib.MINUS_DI(data_frame['%s_High' %self.symbol].values,
                                      data_frame['%s_Low' %self.symbol].values,
                                      data_frame['%s_Close' %self.symbol].values,
                                      timeperiod=self.period)
            data_frame[self.value] = adx
            data_frame[self.plus_di] = plus_di
            data_frame[self.minus_di] = minus_di
        except:
            data_frame[self.value] = np.nan
            data_frame[self.plus_di] = np.nan
            data_frame[self.minus_di] = np.nan

class ULTOSC(TechnicalIndicator):
    def __init__(self, symbol, period1, period2, period3):
        TechnicalIndicator.__init__(self)
        self.symbol = symbol
        self.period1 = period1
        self.period2 = period2
        self.period3 = period3
        self.value = 'ULTOSC_%s_%s_%s_%s' %(symbol, period1, period2, period3)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'ULTOSC(symbol=%s, period1=%s, period2=%s, period3=%s)' %(self.symbol, self.period1, self.period2, self.period3)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            ultosc = talib.ULTOSC(data_frame['%s_High' %self.symbol].values,
                                  data_frame['%s_Low' %self.symbol].values,
                                  data_frame['%s_Close' %self.symbol].values,
                                  timeperiod1=self.period1,
                                  timeperiod2=self.period2,
                                  timeperiod3=self.period3)
            data_frame[self.value] = ultosc
        except:
            data_frame[self.value] = np.nan

class STOCH(TechnicalIndicator):
    def __init__(self, symbol, fast_k_period=5, slow_k_period=3,
                 slow_k_ma_type=talib.MA_Type.SMA, slow_d_period=3,
                 slow_d_ma_type=talib.MA_Type.SMA):
        TechnicalIndicator.__init__(self)
        self.symbol = str(symbol).upper()
        self.fast_k_period = fast_k_period
        self.slow_k_period = slow_k_period
        self.slow_k_ma_type = slow_k_ma_type
        self.slow_d_period = slow_d_period
        self.slow_d_ma_type = slow_d_ma_type
        self.value = 'STOCH_K_%s_%s_%s_%s_%s_%s' %(self.symbol, fast_k_period, slow_k_period, slow_k_ma_type, slow_d_period, slow_d_ma_type)
        self.slowk = self.value
        self.slowd = 'STOCH_D_%s_%s_%s_%s_%s_%s' %(self.symbol, fast_k_period, slow_k_period, slow_k_ma_type, slow_d_period, slow_d_ma_type)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'STOCH(symbol=%s, fast_k_period=%s, slow_k_period=%s, slow_k_ma_type=%s, slow_d_period=%s, self_d_ma_type=%s)' %(self.symbol, self.fast_k_period, self.slow_k_period, self.slow_k_ma_type, self.slow_d_period, self.slow_d_ma_type)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            slowk, slowd = talib.STOCH(data_frame['%s_High' %self.symbol].values,
                                   data_frame['%s_Low' %self.symbol].values,
                                   data_frame['%s_Close' %self.symbol].values,
                                   self.fast_k_period, self.slow_k_period,
                                   self.slow_k_ma_type, self.slow_d_period,
                                   self.slow_d_ma_type)
            data_frame[self.slowk] = slowk
            data_frame[self.slowd] = slowd
        except:
            data_frame[self.slowk] = np.nan
            data_frame[self.slowd] = np.nan

class STOCHF(TechnicalIndicator):
    def __init__(self, symbol, fast_k_period=5, fast_d_period=3,
                 fast_d_ma_type=talib.MA_Type.SMA):
        TechnicalIndicator.__init__(self)
        self.symbol = str(symbol).upper()
        self.fast_k_period = fast_k_period
        self.fast_d_period = fast_d_period
        self.fast_d_ma_type = fast_d_ma_type
        self.value = 'STOCHF_K_%s_%s_%s_%s' %(self.symbol, fast_k_period, fast_d_period, fast_d_ma_type)
        self.fastk = self.value
        self.fastd = 'STOCHF_D_%s_%s_%s_%s' %(self.symbol, fast_k_period, fast_d_period, fast_d_ma_type)
        self.logger.info('Initialized - %s' %self)
    def __str__(self):
        return 'STOCHF(symbol=%s, fast_k_period=%s, fast_d_period=%s, fast_d_ma_type=%s)' %(self.symbol, self.fast_k_period, self.fast_d_period, self.fast_d_ma_type)
    def __repr__(self): return self.value
    def results(self, data_frame):
        try:
            fastk, fastd = talib.STOCHF(data_frame['%s_High' %self.symbol].values,
                                    data_frame['%s_Low' %self.symbol].values,
                                    data_frame['%s_Close' %self.symbol].values,
                                    self.fast_k_period, self.fast_d_period,
                                    self.fast_d_ma_type)
            data_frame[self.fastk] = fastk
            data_frame[self.fastd] = fastd
        except:
            data_frame[self.fastk] = np.nan
            data_frame[self.fastd] = np.nan

class NeuralNetwork(TechnicalIndicator):
    def __init__(self, network, name=None):
        TechnicalIndicator.__init__(self)
        self.network = network
        if name is not None: self.name = name
        else: self.name = str(uuid.uuid4())
        self.value = 'NEURAL_NETWORK_%s' %self.name
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return self.value
    def __repr__(self): return self.value
    def results(self, data_frame):
        data_frame[self.value] = self.network.activate_all(data_frame)

class Ensemble(TechnicalIndicator):
    def __init__(self, ensemble, name=None):
        TechnicalIndicator.__init__(self)
        self.ensemble = ensemble
        if name is not None: self.name = name
        else: self.name = str(uuid.uuid4())
        self.value = 'ENSEMBLE_%s' %self.name
        self.logger.info('Initialized - %s' %self)
    def __str__(self): return self.value
    def __repr__(self): return self.value
    def results(self, data_frame):
        res = self.ensemble.activate_all(data_frame)
        print res
        index = data_frame.index[-len(res):]
        try: data_frame[self.value] = pd.Series(res, index=index)
        except: data_frame[self.value] = np.nan
