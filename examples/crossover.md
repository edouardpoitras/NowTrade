# CrossOver Strategy Example

You can find the working source code of this strategy [here](crossover.py).

_python imports have been omitted in this example, see the source code in the link above_

Let's create our stock list to inform our data connection which stocks to retrieve:

    stocks = StockList(['GOOGL'])

We need a way to reference the individual stock when we create our technical indicators and criteria:

    googl = stocks.get('GOOGL')

This way, we can access different stock values when defining our technical indicators and criteria, such as ```googl.open```, ```googl.close```, etc.  If this doesn't make sense just yet, don't worry, we'll cover technical indicators soon.

Let's specify our start and end dates for this backtest:

    start = datetime.datetime(2010, 01, 01)
    end = datetime.datetime(2015, 01, 01)

We're going to run this strategy from Jan. 1st, 2010, to Jan 1st, 2015.

Now we need to create the dataset that will hold all of the stock data:

    stock_data = Dataset(stocks, YahooConnection(), start, end)

Here we're using the YahooConnection class to pull data from our start datetime to our end datetime.

We could have also used a MongoDatabaseConnection if we had data in a local database.

Note that only 'GOOGL' stock data will be pulled because that's the only stock in our stock list.

At this point, the data hasn't been fetched yet.  We need to fetch the data using the following line of code:

    stock_data.load_data()

You may be wondering why we even bother with the load_data() call.  "Why wouldn't the Dataset object simply load the data when initialized?" or "Why wouldn't the strategy itself take care of loading the data?"

The reason is because this gives us the flexibility of resampling the data before running the strategy, if needed (ie: turning 1min bars into 5min bars).

Now we could do ```stock_data.resample('M')``` to convert the day data to month data.  If we had 1min data we could resample to '5min', '15min', etc.

Alright, let's jump into our technical indicators.

We want a 50-day and 100-day simple moving average of GOOGL close prices

    sma50 = SMA(googl.close, 50)
    sma100 = SMA(googl.close, 100)

There we go!  We could also use the open, high, low, or volume if we wanted to.  For the sake of this example, close will do.  This is why we needed a reference to our googl stock from our stock list earlier.

Now that we've defined our technical indicators, we need to apply them to our dataset:

    stock_data.add_technical_indicator(sma50)
    stock_data.add_technical_indicator(sma100)

At this point all of our technical indicators are calculated and applied to our dataset.  We can examine this pretty easily by accessing the underlying pandas dataframe:

    print stock_data.data_frame.tail()
            GOOGL_Open  GOOGL_High   GOOGL_Low  GOOGL_Close  GOOGL_Volume  \
    Date
    2014-12-24  538.820007  540.289978  535.099976   536.929993        737700
    2014-12-26  536.929993  543.250000  535.489990   541.520020       1110800
    2014-12-29  540.500000  543.929993  537.159973   537.309998       2215000
    2014-12-30  534.960022  537.840027  533.609985   535.280029       1048600
    2014-12-31  537.739990  538.400024  530.200012   530.659973       1232400

            GOOGL_Adj Close  SMA_GOOGL_Close_50  \
    Date
    2014-12-24       536.929993          542.150002
    2014-12-26       541.520020          542.165803
    2014-12-29       537.309998          542.173603
    2014-12-30       535.280029          542.419804
    2014-12-31       530.659973          542.385403

            SMA_GOOGL_Close_100
    Date
    2014-12-24           563.482602
    2014-12-26           563.166402
    2014-12-29           562.794602
    2014-12-30           562.429302
    2014-12-31           561.956502

Click [here](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) for more information on pandas dataframes.

Let's define our entry/exit criteria.  We want to enter a long position when the 50-day moving average crosses over the 100-day moving average.  Thankfully, NowTrade already has a built-in criteria for this named Crossing.

    enter_crit_long = Crossing(sma50.value, 'above', sma100.value)

It simply checks if the technical indicator in the first parameter is crossing 'above' or 'below' the technical indicator in the third parameter.

What about our exit criteria?  Well let's simply apply a trailing stop of 5% below our entry price:

    exit_crit_long = TrailingStop(googl, 0.05, percent=True)

The ```percent=True``` is required or else we'd be using a dollar amount for our trailing stop.

Now let's define what should happen when our criteria are met using criteria groups connected to market actions.
When our entry criteria is true, we want to go long GOOGL.

    enter_crit_group = CriteriaGroup([enter_crit_long], Long(), googl)

Criteria groups take a list of criteria and will fire the action specified in their second parameter only if ALL criteria being checked end up being true in a particular point in time.  In this case, we've created a criteria group that will go ```Long()``` ```googl``` when ```enter_crit_long``` is true.

Let's also add our exit criteria group:

    exit_crit_group = CriteriaGroup([exit_crit_long], LongExit(), googl)

Let's create a trading profile for this simulation.  I'm thinking, $100,000 capital and for now we're just going to put down $10,000 per trade.  We're going to have $10 in fees, but we could easily change this later on.

    profile = TradingProfile(100000, StaticAmount(10000), StaticFee(0))

Well, we're just about ready to run this strategy!  Let's bring it all together:

    strategy = Strategy(stock_data, [enter_crit_group, exit_crit_group], profile)

The Strategy object simply takes our dataset (which now includes all of our technical indicators), a list of criteria groups (which handle checking for our criteria and performing the appropriate actions), and our trading profile.

Let's run it!

    strategy.simulate()
    print strategy.report.pretty_overview()

If you installed the matplotlib python library, you can see some pretty charts with code along the lines of:

    fig = Figure(strategy, rows=3) # Initialize a new figure with 3 rows
    fig.add_chart(googl, row=1) # Show candlesticks on chart 1
    fig.add_chart(googl.volume, row=2, plot_type='bar') # Show bar chart of GOOGL Volume on chart 2
    fig.add_capital_chart(row=3) # Show capital history on chart 3
    fig.show() # Display the figure

See the figures example [here](figures.md).
