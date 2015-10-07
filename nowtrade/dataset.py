"""
The dataset module uses a data connection to retrieve symbol data for strategy
simulation.
"""
import pandas as pd
from nowtrade import logger

class Dataset(object):
    """
    The Dataset object utilizes the pandas DataFrame as a backend for all
    the data handling.
    """
    def __init__(self, symbol_list, data_connection, start_datetime=None, \
                 end_datetime=None, periods=None, granularity=None):
        self.symbol_list = symbol_list
        # Either specify a start and end date or a number of periods since now
        assert periods != None or start_datetime != None
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.periods = periods
        self.granularity = granularity
        self.data_connection = data_connection
        self.data_frame = pd.DataFrame()
        self.technical_indicators = []
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('symbol_list: %s  \
                          data_connection: %s  \
                          start_datetime: %s  \
                          end_datetime: %s  \
                          periods: %s  \
                          granularity: %s'
                         %(symbol_list, \
                           data_connection, \
                           start_datetime, \
                           end_datetime, \
                           periods, \
                           granularity))
    def __str__(self):
        return 'Dataset(symbol_list=%s, data_connection=%s, start_datetime=%s, \
end_datetime=%s, periods=%s, granularity=%s)' \
                       %(self.symbol_list, \
                         self.data_connection, \
                         self.start_datetime, \
                         self.end_datetime, \
                         self.periods, \
                         self.granularity)
    def __repr__(self):
        return 'Dataset(symbol_list=%s, data_connection=%s, start_datetime=%s, \
end_datetime=%s, periods=%s, granularity=%s)' \
                       %(self.symbol_list, \
                         self.data_connection, \
                         self.start_datetime, \
                         self.end_datetime, \
                         self.periods, \
                         self.granularity)

    def load_data(self, realtime=False):
        """
        Does the actual fetching and storage of the data in the
        dataframe attribute.
        """
        for symbol in self.symbol_list:
            self.logger.info('Loading data for %s (realtime=%s)' %(symbol, realtime))
            if self.periods:
                dataframe = self.data_connection.get_data(symbol, \
                                                          self.granularity, \
                                                          self.periods, \
                                                          realtime=realtime)
            else:
                dataframe = self.data_connection.get_data(symbol, \
                                                          self.start_datetime, \
                                                          self.end_datetime)
            self.data_frame = self.data_frame.combine_first(dataframe)

    def resample(self, timeframe, volume=True, adjusted_close=False, symbol=None):
        """
        Resamples data to fit another time frame.
        @type timeframe: string
        @param timeframe: The new timeframe to use; see pandas documentation.
        @type volume: boolean
        @param volume: True if volume should also be resampled.
        @type adjusted_close: boolean
        @param adjusted_close: True if Adj Close should also be resampled.
        @type symbol: Symbol
        @param symbol: The symbol to resample or None for all symbols.
        """
        assert len(self.data_frame) > 0, 'No data loaded yet'
        self.logger.info('Resampling data to %s' %timeframe)
        if symbol:
            self._resample(timeframe, volume, adjusted_close, symbol)
        else: # Do all symbols in symbol list
            for symbol in self.symbol_list:
                self._resample(timeframe, volume, adjusted_close, str(symbol))
            # Drop rows that have all NaN's
            self.data_frame = self.data_frame.dropna(how='all') # Only when ALL columns are NaN
        self.logger.debug('Resampling result: %s' %self.data_frame)

    def _resample(self, timeframe, volume, adjusted_close, symbol):
        """
        Should not use this directly.  Use resample() instead.
        """
        how = {'%s_Open' %symbol: 'first', '%s_High' %symbol: 'max',
               '%s_Low' %symbol: 'min', '%s_Close' %symbol: 'last'}
        if volume:
            how['%s_Volume' %symbol] = 'sum'
        if adjusted_close:
            how['%s_AdjClose' %symbol] = 'last'
        out = self.data_frame.resample(timeframe, how=how)
        self.data_frame['%s_Open' %symbol] = out['%s_Open' %symbol]
        self.data_frame['%s_High' %symbol] = out['%s_High' %symbol]
        self.data_frame['%s_Low' %symbol] = out['%s_Low' %symbol]
        self.data_frame['%s_Close' %symbol] = out['%s_Close' %symbol]
        if volume:
            self.data_frame['%s_Volume' %symbol] = out['%s_Volume' %symbol]
        if adjusted_close:
            self.data_frame['%s_AdjClose' %symbol] = out['%s_AdjClose' %symbol]

    def add_technical_indicator(self, technical_indicator):
        """
        Add the technical indicator to the dataset.
        Must be performed before refering a technical indicator in a
        running strategy.
        """
        self.logger.info('Adding technical indicator: %s' %technical_indicator)
        technical_indicator.results(self.data_frame)
        self.technical_indicators.append(technical_indicator)

    def update_technical_indicators(self):
        """
        Loops through each TI and brings it's values up to the latest time slice
        """
        pass
