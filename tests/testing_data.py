import pandas as pd
from nowtrade.symbol_list import Symbol
from nowtrade.criteria import Criteria
from nowtrade.action import Long, Short, LongExit, ShortExit

"""
MSFT Data
              MSFT_Open  MSFT_High  MSFT_Low  MSFT_Close  MSFT_Volume  MSFT_Adj Close
Date
2010-06-01      25.53      26.31     25.52       25.89     76152400    23.20
2010-06-02      26.06      26.48     25.73       26.46     65718800    23.71
2010-06-03      26.55      26.93     26.41       26.86     67837000    24.07
2010-06-04      26.10      26.57     25.62       25.79     89832200    23.11
2010-06-07      25.82      25.83     25.24       25.29     80456200    22.66
2010-06-08      25.25      25.26     24.65       25.11     87355000    22.50
2010-06-09      25.22      25.52     24.75       24.79     87794000    22.21
2010-06-10      25.13      25.15     24.78       25.00     78930900    22.40
"""

index = pd.bdate_range('20100601', periods=8)
msft_open = [25.53, 26.06, 26.55, 26.10, 25.82, 25.25, 25.22, 25.13]
msft_open_name = 'MSFT_Open'
msft_high = [26.31, 26.48, 26.93, 26.57, 25.83, 25.26, 25.52, 25.15]
msft_high_name = 'MSFT_High'
msft_low = [25.52, 25.73, 26.41, 25.62, 25.24, 24.65, 24.75, 24.78]
msft_low_name = 'MSFT_Low'
msft_close = [25.89, 26.46, 26.86, 25.79, 25.29, 25.11, 24.79, 25.00]
msft_close_name = 'MSFT_Close'
msft_volume = [76152400, 65718800, 67837000, 89832200, 80456200, 87355000, 87794000, 78930900]
msft_volume_name = 'MSFT_Volume'
msft_adj_close = [23.20, 23.71, 24.07, 23.11, 22.66, 22.50, 22.21, 22.40]
msft_adj_close_name = 'MSFT_Adj Close'
msft_data = pd.DataFrame({msft_open_name: msft_open, msft_high_name: msft_high,
                          msft_low_name: msft_low, msft_close_name: msft_close,
                          msft_volume_name: msft_volume, msft_adj_close_name: msft_adj_close},
                          index=index, columns=[msft_open_name, msft_high_name,
                                                msft_low_name, msft_close_name,
                                                msft_volume_name, msft_adj_close_name])

class DummyDataConnection(object):
    """
    For testing purposes.  get_data always returns msft_data.
    """
    def __init__(self): pass
    def get_data(self, *args, **kwargs):
        return msft_data

class DummyCriteria(Criteria):
    """
    For testing purposes.  apply always returns value.
    """
    def __init__(self, value):
        Criteria.__init__(self)
        self.value = value
    def __str__(self):
        return 'DummyCriteria()'
    def __repr__(self): return self.__str__()
    def apply(self, data_frame):
        return self.value
