import numpy as np
import pandas as pd

class Hurst(object):
    """
    < 0.5 == Mean-Reverting
    0.5 == Random Walk
    > 0.5 == Trending
    """
    def __init__(self, y, window, lag=20, x=None):
        self.y = y
        self.lag = lag
        self.window = window
        self.x = x
        self.hedge_ratio = None
        self.results = None

    def run(self):
        assert self.lag > 2, 'Lag must be larger than 2'
        self.data = self.y.copy()
        if self.x is not None:
            ols_result = pd.ols(y=self.y , x=self.x , window=self.window)
            self.hedge_ratio = ols_result.beta['x']
            self.data = ols_result.resid
        lags = range(2, self.lag)
        tau = [np.sqrt(np.std(np.subtract(self.data[lag:], self.data[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        self.results = poly[0]*2.0
        return self.results

if __name__ == '__main__':
    import random
    x = pd.Series([random.random() for _ in range(10000)])
    y = pd.Series([random.random() for _ in range(10000)])
    hurst = Hurst(y, 100, x=x)
    print hurst.run()
    print hurst.hedge_ratio
