from statsmodels.tsa.stattools import adfuller

class ADF(object):
    """
    http://statsmodels.sourceforge.net/stable/generated/statsmodels.tsa.stattools.adfuller.html#statsmodels.tsa.stattools.adfuller
    """
    def __init__(self, data, certainty=90, lag=1):
        self.data = data
        self.certainty = certainty
        self.lag = lag
        self.results = None
        self.value = None
        self.critical_values = None

    def run(self):
        assert self.certainty in [90, 95, 99]
        res = adfuller(self.data, self.lag)
        self.value = res[0]
        self.critical_values = res[4]
        if res[0] < res[4]['%s%%' %(100-self.certainty)]: self.results = True
        else: self.results = False
        return self.results

if __name__ == '__main__':
    import random
    x = [random.random() for _ in range(1000)]
    adf = ADF(x)
    print adf.run()
    print adf.value
    print adf.critical_values
