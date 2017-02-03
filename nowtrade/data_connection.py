"""
A nowtrade module to enables pulling stock/currency data from external sources.
Also makes it easy to store this data locally for future strategy testing.
"""
import urllib2
import zipfile
import datetime
import pandas as pd
import pandas_datareader.data as web
from pandas import read_csv
from StringIO import StringIO
from nowtrade import logger

class NoDataException(Exception):
    """
    Exception used when no data could be gathered from a data connection.
    """
    pass

class DataConnection(object):
    """
    Base class for all data connections.
    """
    def __init__(self):
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('Initialized')
    def __str__(self):
        return self.__class__.__name__

class YahooConnection(DataConnection):
    """
    Utilizes Pandas' Remote Data Access methods to fetch
    symbol data from Yahoo.
    """
    def get_data(self, symbol, start, end):
        """
        @type symbol: string
        @type start: datetime
        @type end: datetime
        @return: Returns a pandas DataFrame of the requested symbol
        @rtype: pandas.DataFrame
        """
        ret = web.DataReader(str(symbol).upper(), 'yahoo', start, end)
        ret.rename(columns=lambda name: '%s_%s' %(symbol, name), inplace=True)
        return ret

class GoogleConnection(DataConnection):
    """
    Utilizes Pandas' Remote Data Access methods to fetch
    symbol data from Google.
    """
    def _request(self, url):
        """
        Used for custom request outside of Pandas framework.
        """
        try:
            return urllib2.urlopen(url)
        except urllib2.HTTPError, error:
            print 'Error when connecting to Google servers: %s' %error
        except IOError, error:
            print 'Could not connect to Google servers with url %s: %s' %(url, error)
        except Exception, error: # pylint: disable=broad-except
            print 'Unknown Error when trying to connect to Google servers: %s' %error

    def get_data(self, symbol, start, end, symbol_in_column=True):
        """
        @type symbol: string
        @type start: datetime
        @type end: datetime
        @return: Returns a pandas DataFrame of the requested symbol
        @rtype: pandas.DataFrame
        """
        ret = web.DataReader(str(symbol).upper(), 'google', start, end)
        if symbol_in_column:
            ret.rename(columns=lambda name: '%s_%s' %(symbol, name), inplace=True)
        return ret

    def get_ticks(self, symbol, period='15d', interval=60, symbol_in_column=True):
        """
        Always returns 15 days worth of 1min data.
        Get tick prices for the given ticker symbol.
        @param symbol: symbol symbol
        @type symbol: string
        """
        symbol = str(symbol).upper()
        data = None # Return data
        if True:
            url = 'http://www.google.com/finance/getprices?i=%s&p=%s&f=d,o,h,l,c,v&q=%s' \
                   %(interval, period, symbol)
            page = self._request(url)
            entries = page.readlines()[7:] # first 7 line is document information
            days = [] # Keep track of all days
            day = None # Keep track of current day
            date = None # Keep track of current time
            # sample values:'a1316784600,31.41,31.5,31.4,31.43,150911'
            for entry in entries:
                quote = entry.strip().split(',')
                if quote[0].startswith('a'): # Datetime
                    day = datetime.datetime.fromtimestamp(int(quote[0][1:]))
                    days.append(day)
                    date = day
                else:
                    date = day + datetime.timedelta(minutes=int(quote[0])*interval/60)
                if symbol_in_column:
                    data_frame = pd.DataFrame({'%s_Open' %symbol: float(quote[4]), \
                                               '%s_High' %symbol: float(quote[2]), \
                                               '%s_Low' %symbol: float(quote[3]), \
                                               '%s_Close' %symbol: float(quote[1]), \
                                               '%s_Volume' %symbol: int(quote[5])}, \
                                              index=[date])
                else:
                    data_frame = pd.DataFrame({'Open': float(quote[4]), \
                                               'High': float(quote[2]), \
                                               'Low': float(quote[3]), \
                                               'Close': float(quote[1]), \
                                               'Volume': int(quote[5])}, \
                                              index=[date])
                if data is None:
                    data = data_frame
                else: data = data.combine_first(data_frame)
            # Reindex for missing minutes
            new_index = None
            for day in days:
                index = pd.date_range(start=day, periods=391, freq='1Min')
                if new_index is None:
                    new_index = index
                else:
                    new_index = new_index + index
            # Front fill for minute data
            return data.reindex(new_index, method='ffill')

class OandaConnection(DataConnection):
    """
    Data connection used to gather data from the Oanda forex broker.
    """
    def __init__(self, account_id, access_token, environment='practice'):
        DataConnection.__init__(self)
        import oandapy # pylint: disable=import-error
        self.account_id = account_id
        self.environment = environment
        self.oanda = oandapy.API(environment=environment, access_token=access_token)
    def __str__(self):
        return 'OandaConnection(account_id=%s, access_token=******, environment=%s)' \
                                %(self.account_id, self.environment)
    def __repr__(self):
        return 'OandaConnection(account_id=%s, access_token=******, environment=%s)' \
                                %(self.account_id, self.environment)

    def get_data(self, symbol, granularity='H1', periods=5000, \
                       realtime=False, symbol_in_column=True):
        """
        Gets the dataframe containing all of the currency data requested.
        """
        self.logger.info('Getting %s candles of %s data for %s granularity \
                          (realtime=%s, symbol_in_column=%s)' \
                          %(periods, symbol, granularity, realtime, symbol_in_column))
        candles = self.oanda.get_history(account_id=self.account_id,
                                         instrument=symbol,
                                         granularity=granularity,
                                         count=periods)['candles']
        if not realtime:
            candles.pop()
        data = None
        for candle in candles:
            date = datetime.datetime.strptime(candle['time'], "%Y-%m-%dT%H:%M:%S.000000Z")
            if symbol_in_column:
                data_frame = pd.DataFrame({'%s_Open' %symbol: candle['openBid'], \
                                           '%s_High' %symbol: candle['highBid'], \
                                           '%s_Low' %symbol: candle['lowBid'], \
                                           '%s_Close' %symbol: candle['closeBid'], \
                                           '%s_Volume' %symbol: candle['volume']}, \
                                          index=[date])
            else:
                data_frame = pd.DataFrame({'Open' %symbol: candle['openBid'], \
                                           'High' %symbol: candle['highBid'], \
                                           'Low' %symbol: candle['lowBid'], \
                                           'Close' %symbol: candle['closeBid'], \
                                           'Volume' %symbol: candle['volume']}, \
                                          index=[date])
            if data is None:
                data = data_frame
            else:
                data = data.combine_first(data_frame)
        self.logger.debug('Data: %s' %data)
        return data

class ForexiteConnection(DataConnection):
    """
    Forexite 1min data
    """
    URL = "http://www.forexite.com/free_forex_quotes/%s/%s/%s%s%s.zip"
    #URL = "http://www.forexite.com/free_forex_quotes/YY/MM/DDMMYY.zip"
    def get_data(self, start, end):
        """
        Always returns 1min OPEN, HIGH, LOW, CLOSE for all available currency
        pairs on the Forexite website.  No Volume information.
        """
        assert start <= end
        data = {}
        # One day at a time
        while start <= end:
            day = str(start.day)
            if len(day) == 1:
                day = '0%s' %day
            month = str(start.month)
            if len(month) == 1:
                month = '0%s' %month
            long_year = str(start.year)
            year = long_year[2:]
            url = self.URL %(long_year, month, day, month, year)
            start = start + datetime.timedelta(1)
            try:
                page = urllib2.urlopen(url)
            except urllib2.HTTPError, error:
                print error
                continue
            zipf = zipfile.ZipFile(StringIO(page.read()))
            series = read_csv(zipf.open('%s%s%s.txt' %(day, month, year)), parse_dates=True)
            for ticker in series['<TICKER>'].unique():
                data_frame = series.loc[series['<TICKER>'] == ticker]  # pylint: disable=no-member
                first_row = data_frame.iloc[0]
                start_date = first_row['<DTYYYYMMDD>']
                start_time = first_row['<TIME>']
                data_frame.index = pd.date_range(str(start_date) + ' ' + \
                                   str(start_time).zfill(6), \
                                   periods=len(data_frame), \
                                   freq='1Min')
                del data_frame['<TICKER>']
                del data_frame['<DTYYYYMMDD>']
                del data_frame['<TIME>']
                rename_columns = lambda name: '%s_%s' %(ticker, name.strip('<>').capitalize()) # pylint: disable=cell-var-from-loop
                data_frame.rename(columns=rename_columns, inplace=True)
                if ticker in data:
                    data[ticker] = data[ticker].combine_first(data_frame)
                else:
                    data[ticker] = data_frame
        return data

class MySQLConnection(DataConnection):
    """
    MySQL database connection to retrieve data.
    """
    def __init__(self, host='localhost', port=3306, database='symbol_data', \
                 username='root', password=''):
        DataConnection.__init__(self)
        import MySQLdb
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.db = MySQLdb.connect(host=host,
                                  port=port,
                                  user=username,
                                  passwd=password,
                                  db=database)
        self.cursor = self.db.cursor()

    def get_data(self, table_name, start, end, volume=False,
                 timestamp_column='timestamp', custom_cols=[], label_prefix=''):
        """
        Returns a dataframe of the symbol data requested.

        Assumes you have column names matching the following:

            timestamp, open, high, low, close, volume

        Volume is optional.

        custom_cols is a list of custom column names you want to pull in on top
        of the OHLCV data.
        """
        query = 'SELECT %s, open, high, low, close' %timestamp_column
        if volume:
            query += ', volume'
        for col in custom_cols:
            query += ', %s' %col
        query += ' FROM %s WHERE %s >= "%s" AND %s <= "%s"'
        query = query %(table_name,
                        timestamp_column,
                        start,
                        timestamp_column,
                        end)
        num_results = self.cursor.execute(query)
        if num_results < 1:
            raise NoDataException()
        results = []
        for result in self.cursor.fetchall():
            row = {'%sDate' %label_prefix: result[0],
                   '%sOpen' %label_prefix: result[1],
                   '%sHigh' %label_prefix: result[2],
                   '%sLow' %label_prefix: result[3],
                   '%sClose' %label_prefix: result[4]}
            index = 4
            if volume:
                index += 1
                row['%sVolume' %label_prefix] = result[index]
            for col in custom_cols:
                index += 1
                row['%s%s' %(label_prefix, col)] = result[index]
            results.append(row)
        ret = pd.DataFrame.from_dict(results)
        return ret.set_index('%sDate' %label_prefix)

class MongoDatabaseConnection(DataConnection):
    """
    MongoDB connection to retrieve data.
    """
    def __init__(self, host='127.0.0.1', port=27017, database='symbol-data', \
                 username=None, password=None):
        DataConnection.__init__(self)
        from pymongo import MongoClient
        self.connection = None
        self.database = None
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = MongoClient(host, port)
        self.database = self.connection[database]

    def get_data(self, symbol, start, end, symbol_in_column=True):
        """
        Returns a dataframe of the symbol data requested.
        """
        from pymongo import ASCENDING
        symbol = str(symbol).upper()
        results = self.database[symbol].find({'_id': \
                              {'$gte': start, '$lte': end}}\
                              ).sort('datetime', ASCENDING)
        ret = pd.DataFrame.from_dict(list(results))
        if len(ret) < 1:
            raise NoDataException()
        ret.rename(columns={'open': 'Open', \
                            'high': 'High', \
                            'low': 'Low', \
                            'close': 'Close', \
                            'volume': 'Volume', \
                            'adj_close': 'Adj Close', \
                            '_id': 'Date'}, \
                           inplace=True)
        ret = ret.set_index('Date')
        if symbol_in_column:
            ret.rename(columns=lambda name: '%s_%s' %(symbol, name), inplace=True)
        return ret

    def set_data(self, data_frame, symbols, volume=True, adj_close=True):
        """
        Stores Open, Close, High, Low, Volume, and Adj Close of
        symbols specified using the data in the DataFrame provided.
        Typically you'd pull data using another connection and
        feed it's data_frame to this function in order to store
        the data in a local MongoDB.
        """
        for symbol in symbols:
            symbol = str(symbol).upper()
            if adj_close:
                data = data_frame.loc[:, ['%s_Open' %symbol, \
                                          '%s_Close' %symbol, \
                                          '%s_High' %symbol, \
                                          '%s_Low' %symbol, \
                                          '%s_Volume' %symbol, \
                                          '%s_Adj Close' %symbol]]
                data.columns = ['open', 'close', 'high', 'low', 'volume', 'adj_close']
            elif volume:
                data = data_frame.loc[:, ['%s_Open' %symbol, \
                                          '%s_Close' %symbol, \
                                          '%s_High' %symbol, \
                                          '%s_Low' %symbol, \
                                          '%s_Volume' %symbol]]
                data.columns = ['open', 'close', 'high', 'low', 'volume']
            else:
                data = data_frame.loc[:, ['%s_Open' %symbol, \
                                          '%s_Close' %symbol, \
                                          '%s_High' %symbol, \
                                          '%s_Low' %symbol]]
                data.columns = ['open', 'close', 'high', 'low']
            for row in data.iterrows():
                values = dict(row[1])
                values['_id'] = row[0]
                self.database[symbol].insert(values)

def populate_mongo_day(symbols, start, end, database='symbol-data'):
    """
    Helper function to populate a local mongo db with daily stock data.
    Uses the YahooConnection class.
    """
    mgc = MongoDatabaseConnection(database=database)
    for symbol in symbols:
        symbol = symbol.upper()
        yahoo = YahooConnection()
        try:
            data = yahoo.get_data(symbol, start, end)
            mgc.set_data(data, [symbol])
        except Exception, error: # pylint: disable=broad-except
            print 'Error for %s (%s - %s): %s' %(symbol, start, end, error)

def populate_mongo_minute(symbols, period='15d', database='symbol-data-1min'):
    """
    Helper function to populate a local mongo db with minute stock data.
    Uses the GoogleConnection class.
    """
    mgc = MongoDatabaseConnection(database=database)
    for symbol in symbols:
        google = GoogleConnection()
        try:
            data = google.get_ticks(symbol, period=period)
            mgc.set_data(data, [symbol], adj_close=False)
        except Exception, error: # pylint: disable=broad-except
            print 'Failed %s: %s' %(symbol, error)

def populate_currency_minute(start, end, sleep=None, database='symbol-data-1min-currency'):
    """
    Helper function to populate a local mongo db with currency minute data.
    Uses the ForexiteConnection class.
    """
    mgc = MongoDatabaseConnection(database=database)
    forexite = ForexiteConnection()
    if sleep:
        import time
    while start <= end:
        data = forexite.get_data(start, start)
        for ticker in data:
            mgc.set_data(data[ticker], [ticker], volume=False, adj_close=False)
        start += datetime.timedelta(1)
        if sleep:
            time.sleep(sleep)

def populate_oanda_currency(account_id, access_token, symbols, granularity='M5', \
                            periods=5000, database='symbol-data-5min-currency'):
    """
    Helper function to populate a local mongo db with currency minute data.
    Uses the OandaConnection class.
    """
    mgc = MongoDatabaseConnection(database=database)
    oanda = OandaConnection(account_id, access_token)
    for symbol in symbols:
        data = oanda.get_data(symbol, granularity=granularity, periods=periods)
        mgc.set_data(data, [symbol], adj_close=False)

def convert_1min_to_5min(db_name_1min, db_name_5min, symbols, start, end, volume=False):
    """
    Helper function to convert 1min data to 5min data.
    Specify the 1min database you want to convert, the 5min database to be
    created, the list of symbols, the start and end datetimes, and whether
    or not to include volume in the resampling.
    """
    import nowtrade.dataset
    mgc_old = MongoDatabaseConnection(database=db_name_1min)
    mgc_new = MongoDatabaseConnection(database=db_name_5min)
    dataset = nowtrade.dataset.Dataset(symbols, mgc_old, start, end)
    dataset.load_data()
    dataset.resample('5Min', volume=volume)
    mgc_new.set_data(dataset.data_frame, symbols, volume=volume, adj_close=False)

def convert_5min_to_15min(db_name_5min, db_name_15min, symbols, start, end, volume=False):
    """
    Helper function to convert 1min data to 5min data.
    Specify the 5min database you want to convert, the 15min database to be
    created, the list of symbols, the start and end datetimes, and whether
    or not to include volume in the resampling.
    """
    import nowtrade.dataset
    mgc_old = MongoDatabaseConnection(database=db_name_5min)
    mgc_new = MongoDatabaseConnection(database=db_name_15min)
    dataset = nowtrade.dataset.Dataset(symbols, mgc_old, start, end)
    dataset.load_data()
    dataset.resample('15Min', volume=volume)
    mgc_new.set_data(dataset.data_frame, symbols, volume=volume, adj_close=False)
