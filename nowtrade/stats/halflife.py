import numpy as np
from statsmodels.api import OLS

def halflife(data):
    d = data.shift(1)
    delta = data - d
    del delta[0]
    del d[0]
    regress_results = OLS(delta, d).fit()
    return -np.log(2) / regress_results.params[0]

if __name__ == '__main__':
    import pandas as pd
    import random
    data = pd.Series([random.random() for x in range(1000)])
    print halflife(data)
