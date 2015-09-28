# DataConnection Examples
Let's pull some data from Yahoo and store it in our local instance of mongo.

You could simply use the Yahoo servers without saving it in mongo, but this way is faster for strategy testing/iteration.

You can use the helper scripts in the [scripts](../scripts) folder for this, but here we will do it manually:

    $ python
    >>> import datetime
    >>> from nowtrade import data_connection
    >>> stocks = ['AAPL']
    >>> start = datetime.datetime(2015, 01, 01)
    >>> end = datetime.datetime(2015, 01, 10)
    >>> data_connection.populate_mongo_day(stocks, start, end, db='stock-data')

```populate_mongo_day()``` is a helper function that pulls data from Yahoo and stores it in our local instance of mongo.
You can use this function as often as you like with a later end date without overriding existing data.

    >>> exit()

Let's go check out our new data

    $ mongo
    > show dbs
    admin        (empty)
    local        0.078GB
    stock-data  0.078GB

There's our new stock-data database.  Let's see what collections it holds:

    > use stock-data
    > show collections
    AAPL
    system.indexes

There's the AAPL collection holding AAPL stock data from Jan 1st to Jan 10th.  Let's spit out some values:

    > db.AAPL.find()
    { "_id" : ISODate("2015-01-02T00:00:00Z"), "volume" : 53204600, "adj_close" : 107.958556, "high" : 111.440002, "low" : 107.349998, "close" : 109.33000200000001, "open" : 111.389999 }
    { "_id" : ISODate("2015-01-05T00:00:00Z"), "volume" : 64285500, "adj_close" : 104.91718999999999, "high" : 108.650002, "low" : 105.410004, "close" : 106.25, "open" : 108.290001 }
    { "_id" : ISODate("2015-01-06T00:00:00Z"), "volume" : 65797100, "adj_close" : 104.927067, "high" : 107.43, "low" : 104.629997, "close" : 106.260002, "open" : 106.540001 }
    { "_id" : ISODate("2015-01-07T00:00:00Z"), "volume" : 40105900, "adj_close" : 106.398374, "high" : 108.199997, "low" : 106.699997, "close" : 107.75, "open" : 107.199997 }
    { "_id" : ISODate("2015-01-08T00:00:00Z"), "volume" : 59364500, "adj_close" : 110.48644099999999, "high" : 112.150002, "low" : 108.699997, "close" : 111.889999, "open" : 109.230003 }
    { "_id" : ISODate("2015-01-09T00:00:00Z"), "volume" : 53699500, "adj_close" : 110.60493799999999, "high" : 113.25, "low" : 110.209999, "close" : 112.010002, "open" : 112.66999799999999 }

Awesome.  Now we can use the faster MongoDatabaseConnection() instead of the YahooConnection().  You can now run strategies without being connected to the internet!

For help using mongo, see the MongoDB [documentation](http://docs.mongodb.org/manual/) page

    > exit

Let's see some examples of using our local data instead of the YahooConnection():

    $ python
    >>> import datetime
    >>> from nowtrade.data_connection import MongoDatabaseConnection, YahooConnection, GoogleConnection, OandaConnection, ForexiteConnection

MongoDatabaseConnection() is a connection to your local mongo db with your new data

YahooConnection() is used for stock daily data

GoogleConnection() is used for stock daily and minute data

ForexiteConnection() and OandaConnection() are used for currency data

By looking through the data_connections.py file, you can see that's it's pretty easy to add more of these.

When developing strategies you won't normally be using the get_data function directly, but it's nice to be able to see what data you're dealing with.

    >>> yahoo = YahooConnection()
    >>> yahoo.get_data('AAPL', datetime.datetime(2015, 01, 01), datetime.datetime(2015, 01, 10))
                 AAPL_Open   AAPL_High    AAPL_Low  AAPL_Close  AAPL_Volume  \
    Date
    2015-01-02  111.389999  111.440002  107.349998  109.330002     53204600
    2015-01-05  108.290001  108.650002  105.410004  106.250000     64285500
    2015-01-06  106.540001  107.430000  104.629997  106.260002     65797100
    2015-01-07  107.199997  108.199997  106.699997  107.750000     40105900
    2015-01-08  109.230003  112.150002  108.699997  111.889999     59364500
    2015-01-09  112.669998  113.250000  110.209999  112.010002     53699500

            AAPL_Adj Close
    Date
    2015-01-02      107.958556
    2015-01-05      104.917190
    2015-01-06      104.927067
    2015-01-07      106.398374
    2015-01-08      110.486441
    2015-01-09      110.604938

    >>> google = GoogleConnection()
    >>> google.get_data('AAPL', datetime.datetime(2015, 01, 01), datetime.datetime(2015, 01, 10))
                AAPL_Open  AAPL_High  AAPL_Low  AAPL_Close  AAPL_Volume
    Date
    2015-01-02     111.39     111.44    107.35      109.33     53204626
    2015-01-05     108.29     108.65    105.41      106.25     64285491
    2015-01-06     106.54     107.43    104.63      106.26     65797116
    2015-01-07     107.20     108.20    106.70      107.75     40105934
    2015-01-08     109.23     112.15    108.70      111.89     59364547
    2015-01-09     112.67     113.25    110.21      112.01     53699527

    >>> mongo = MongoDatabaseConnection()
    >>> mongo.get_data('AAPL', datetime.datetime(2015, 01, 01), datetime.datetime(2015, 01, 10))
            AAPL_Adj Close  AAPL_Close   AAPL_High    AAPL_Low   AAPL_Open  \
    Date
    2015-01-02      107.958556  109.330002  111.440002  107.349998  111.389999
    2015-01-05      104.917190  106.250000  108.650002  105.410004  108.290001
    2015-01-06      104.927067  106.260002  107.430000  104.629997  106.540001
    2015-01-07      106.398374  107.750000  108.199997  106.699997  107.199997
    2015-01-08      110.486441  111.889999  112.150002  108.699997  109.230003
    2015-01-09      110.604938  112.010002  113.250000  110.209999  112.669998

            AAPL_Volume
    Date
    2015-01-02     53204600
    2015-01-05     64285500
    2015-01-06     65797100
    2015-01-07     40105900
    2015-01-08     59364500
    2015-01-09     53699500

    >>> google.get_ticks('AAPL', period='15d', interval=60)
                     AAPL_Close  AAPL_High  AAPL_Low  AAPL_Open  AAPL_Volume
    2015-09-03 09:30:00    112.4000   112.5100  112.3800   112.4900       438787
    2015-09-03 09:31:00    112.1200   112.4600  111.9000   112.4200       400870
    2015-09-03 09:32:00    112.6000   112.6000  111.9000   112.1200       608089
    ...
    2015-09-23 15:58:00    114.4450   114.5600  114.4410   114.5500       171884
    2015-09-23 15:59:00    114.4750   114.5000  114.4400   114.4400       153935
    2015-09-23 16:00:00    114.3200   114.5100  114.3200   114.4700      1550845
    [5474 rows x 5 columns]

The data returned by the data connection will always be in a pandas [dataframe](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) format.
