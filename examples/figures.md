# Figures Example

You can find the working source code of this strategy [here](figures.py).

_python imports have been omitted in this example, see the source code in the link above_

The NowTrade ```Figure``` object is very useful for quickly charting elements of your strategy.  It is a simple wrapper around matplotlib's plotting mechanism and requires the matplotlib library to be installed.

Here's a simple example displaying GOOGL candlesticks from Jan. 1st 2014 to Jan. 1st 2015:

    stocks = StockList(['GOOGL'])
    googl = stocks.get('GOOGL')
    start = datetime.datetime(2014, 01, 01)
    end = datetime.datetime(2015, 01, 01)
    stock_data = Dataset(stocks, YahooConnection(), start, end)
    fig = Figure(stock_data)
    fig.add_chart(googl)
    fig.show()

Let's use a more practical example with a simple strategy where we want to display the following in four different charts:

  -  GOOGL candlesticks with the actions taken by the strategy
  -  GOOGL volume
  -  Technical indicators
  -  Capital history

For this example we will use the following strategy:

    stocks = StockList(['GOOGL'])
    googl = stocks.get('GOOGL')
    start = datetime.datetime(2013, 01, 01)
    end = datetime.datetime(2015, 01, 01)
    stock_data = Dataset(stocks, MongoDatabaseConnection(), start, end)
    stock_data.load_data()
    sma10 = SMA(googl.close, 10)
    sma25 = SMA(googl.close, 25)
    stock_data.add_technical_indicator(sma10)
    stock_data.add_technical_indicator(sma25)
    enter_crit_long = CrossingAbove(sma10, sma25)
    exit_crit_long = TrailingStop(googl, 0.05, percent=True)
    enter_crit_group = CriteriaGroup([enter_crit_long], Long(), googl)
    exit_crit_group = CriteriaGroup([exit_crit_long], LongExit(), googl)
    profile = TradingProfile(100000, StaticAmount(10000), StaticFee(5))
    strategy = Strategy(stock_data, [enter_crit_group, exit_crit_group], profile)
    strategy.simulate()

The ```Figure``` object accepts two parameters:

  1. The ```dataset``` OR ```strategy``` object to use when charting
  2. The number of charts that will be plotted on this figure

In the previous example, we gave the ```Figure``` object a dataset.  It had no context on any strategy.  In this example, we will feed it a strategy and it will be smart enough to chart the strategy actions along with the candlesticks.

We also know that we now want four charts instead of the one from the previous example.  Let's see what that looks like:

    fig = figures.Figure(strategy, rows=4)

There we go.  Now the figure expects four charts (one on top of the other) with the same x-axis of datetime.

Let's add our candlesticks:

    fig.add_chart(googl)

The ```add_chart()``` function takes a stock symbol for candlestick charting, or a technical indicator for standard line or bar charts.

    fig.add_chart(googl.volume, row=2, plot_type='bar')

Here we are telling our figure to show the GOOGL volume on the second figure, and we want it to be a bar chart.  The default for row is ```row=1``` and plot_type is ```plot_type='line'```.

Let's add our two technical indicators in the third chart:

    fig.add_chart(sma10, row=3)
    fig.add_chart(sma25, row=3, color='red')

Here we are adding both technical indicators to our third chart, but we are also specifying that the SMA25 technical indicator should appear as a red line instead of the default color ```color='blue'```.

The last chart will hold our capital history throughout our strategy:

    fig.add_capital_chart(row=4)

The ```add_capital_chart()``` is a special function used to chart the capital history of a strategy as we don't have access to this information in a technical indicator.  It defaults to ```color='green'``` and always has a ```plot_type``` of ```line```.  It can not be used when a dataset has been provided to the figure object instead of a strategy.

Let's go ahead and display our new figure:

    fig.show()

And there we have it!  Hopefully this can be useful when finding new successful strategies.
