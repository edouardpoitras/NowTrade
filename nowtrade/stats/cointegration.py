import pandas as pd
from statsmodels.api import OLS
from statsmodels.tsa.stattools import adfuller

class CADF(object):
    def __init__(self, y, x, lookback, certainty=90, max_lag=None):
        self.y = y
        self.x = x
        self.lookback = lookback
        self.certainty = certainty
        self.max_lag = max_lag
        self.pairs = pd.DataFrame({'y': self.y, 'x': self.x})
        self.result = None
        self.value = None
        self.critical_values = None

    def run(self, calculate_zscore=True):
        assert self.certainty in [90, 95, 99]
        ols_result = pd.ols(y=self.y, x=self.x, window=self.lookback)
        self.pairs['hedge_ratio'] = ols_result.beta['x']
        if calculate_zscore: self.calculate_zscore()
        self.pairs.dropna()
        adf, pvalue, usedlag, nobs, critical_values, icbest = adfuller(ols_result.resid, maxlag=self.max_lag)
        self.value = adf
        self.critical_values = critical_values
        if adf <= critical_values['%s%%' %(100-self.certainty)]: self.result = True
        else: self.result = False
        return self.result

    def calculate_zscore(self):
        self.pairs['spread'] = self.y - self.pairs['hedge_ratio'] * self.x
        self.pairs['zscore'] = (self.pairs['spread'] - pd.rolling_mean(self.pairs['spread'], self.lookback)) / pd.rolling_std(self.pairs['spread'], self.lookback)

if __name__ == '__main__':
    import random
    x = pd.Series([random.random() for _ in range(20000)])
    y = pd.Series([random.random() + 20 for _ in range(20000)])
    cadf = CADF(y, x, 100)
    print cadf.run()
    print cadf.value
    print cadf.critical_values
    print cadf.pairs
