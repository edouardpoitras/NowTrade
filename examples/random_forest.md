# Random Forest Strategy Example

##### The user may want to educate themselves on potential issues with machine learning based strategies before using them in live trading, such as overfitting/underfitting, biases, etc. This is a very broad subject that is not covered here.

You can find the working source code of this strategy [here](random_forest.py).

_python imports have been omitted in this example, see the source code in the link above_

Let's create our stock list to inform our data connection which stocks to retrieve:

    stock_data = symbol_list.StockList(['GOOGL'])

We need a way to reference the individual stock when we create our technical indicators and criteria:

    symbol = stocks.get('GOOGL')

This way, we can access different stock values when defining our technical indicators and criteria, such as ```symbol.open```, ```symbol.close```, etc.  If this doesn't make sense just yet, don't worry, we'll cover technical indicators soon.

Let's specify our start and end dates for training our ensemble.  It's important that our train and test data are different.  In this case, we will use 5 years of training data from 2010 to 2015, and 6 months of testing data from Jan 2015 to Jul 2015.

    train_start = datetime.datetime(2010, 01, 01)
    train_end = datetime.datetime(2015, 01, 01)
    test_start = train_end
    test_end = datetime.datetime(2015, 07, 01)

Now we need to create the datasets that will hold all of the stock data.  First, our training dataset:

    train_dataset = dataset.Dataset(stocks, YahooConnection(), train_start, train_end)

Here we're using the YahooConnection class to pull data from our start datetime to our end datetime.

We could have also used a MongoDatabaseConnection if we had data in a local database.

Note that only 'GOOGL' stock data will be pulled because that's the only stock in our stock list.

At this point, the data hasn't been fetched yet.  We need to fetch the data using the following line of code:

    train_dataset.load_data()

You may be wondering why we even bother with the load_data() call.  "Why wouldn't the Dataset object simply load the data when initialized?"

The reason is because this gives us the flexibility of resampling the data before running the strategy, if needed (eg: turning 1min bars into 5min bars).

Now we could do ```stock_data.resample('M')``` to convert the day data to month data.  If we had 1min data we could resample to '5min', '15min', etc.

Although we don't need to do this now, let's also load up our testing data while we're covering datasets:

    test_dataset = dataset.Dataset(stocks, YahooConnection(), test_start, test_end)
    test_dataset.load_data()

Alright, let's create our random forest ensemble.  We will Use the OHLCV data of the stock to predict the close price in the future.

    rf = ensemble.Ensemble([symbol.open, symbol.high, symbol.low, symbol.close, symbol.volume], [symbol.close])

There we go!  This is also why we needed a reference to our googl stock from our stock list earlier.

We don't absolutely need to use the 'GOOGL' values to train our ensemble.  We could also have used other stock values, indexes (if they were loaded in our dataset), technical indicators like RSI, SMA, or even other random forest ensembles!  As long as the stock was in our StockList and we have a reference to the technical indicators that have been added to our dataset, we can utilize them in our data for training.

We're not quite done creating our ensemble though.  We still need to configure it with all the nice bells and whistles that ensembles require. We're going to use a 5 day prediction window for our stock's close price and a look back period of 25. The look back period is the number of bars moving backwards in time that will be used for the training and predictions. Typically, you will need to tweak these parameters quite a bit to find the right strategy for you.  For more configuration options with these, see the scikit-learn Ensemble [documentation](http://scikit-learn.org/stable/modules/ensemble.html#parameters).

    rf.build_ensemble(train_dataset, prediction_window=5, look_back_window=25, number_of_jobs=2)

In this case we're also using the ```number_of_jobs``` parameter, which refers to the number of CPU threads to use when fitting the model.

Now let's fit the model - this could take a while depending on how much data you're using:

    rf.fit()

I recommend saving your random forest immediately after training for every strategy.  This way, if you stumble upon a really good one, you can load it up and use it for real trading.

    rf.save_to_file('test.ens')

We can load the ensemble using the following line of code

    rf = ensemble.load_from_file('test.ens')

Typically, this is the part where I would create the testing data set, but we've already done this above.  Let's attach our newly fitted ensemble to a technical indicator so it can be used with our criteria.

    random_forest = technical_indicator.Ensemble(rf)
    test_dataset.add_technical_indicator(random_forest)

Our random forest technical indicator will spit out prediction prices, but we still need a threshold to determine whether or not we want to enter the trade.  Let's define a technical indicator that is $5 higher than the ensemble's prediction, and one that is $5 lower.

_Note that we could have also simply used a Position criteria on the ensemble price and skipped the threshold step entirely._

    threshold_above = technical_indicator.Addition(random_forest.value, 5)
    test_dataset.add_technical_indicator(threshold_above)

    threshold_below = technical_indicator.Subtraction(random_forest.value, 5)
    test_dataset.add_technical_indicator(threshold_below)

Now we can check if the ensemble's prediction is $5 higher or lower than the current price, and take action!

Before we move on, it would be beneficial to see what the underlying pandas dataframe looks like:

    print test_dataset.data_frame.tail()

                GOOGL_Open  GOOGL_High   GOOGL_Low  GOOGL_Close  GOOGL_Volume  \
    Date
    2015-06-25  560.299988  563.140015  557.460022   557.950012       1334200
    2015-06-26  559.710022  560.000000  551.849976   553.059998       2127800
    2015-06-29  546.750000  550.900024  540.239990   541.250000       1876800
    2015-06-30  545.090027  545.900024  539.539978   540.039978       1897100
    2015-07-01  543.659973  545.809998  539.760010   543.299988       1532900

                GOOGL_Adj Close  ENSEMBLE_d07063a4-87eb-42db-bcd4-dfa279e93625  \
    Date
    2015-06-25       557.950012                                     552.051128
    2015-06-26       553.059998                                     551.441918
    2015-06-29       541.250000                                     538.643696
    2015-06-30       540.039978                                     532.812764
    2015-07-01       543.299988                                     527.262415

                ADDITION_ENSEMBLE_d07063a4-87eb-42db-bcd4-dfa279e93625_5  \
    Date
    2015-06-25                                         557.051128
    2015-06-26                                         556.441918
    2015-06-29                                         543.643696
    2015-06-30                                         537.812764
    2015-07-01                                         532.262415

                SUBTRACTION_ENSEMBLE_d07063a4-87eb-42db-bcd4-dfa279e93625_5
    Date
    2015-06-25                                         547.051128
    2015-06-26                                         546.441918
    2015-06-29                                         533.643696
    2015-06-30                                         527.812764
    2015-07-01                                         522.262415

Click [here](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) for more information on pandas dataframes.

  And there you have it!  You can clearly see what the ensemble predictions where on each day by looking at the ```ENSEMBLE_<uuid>``` column.  The ```ADDITION_ENSEMBLE_<uuid>_5``` and ```SUBTRACTION_ENSEMBLE_<uuid>_5``` are clearly +/- $5 from our ensemble prediction values, and we can use those prices as our threshold for trading.

Let's create our trading criteria, starting with some entry criteria.  We want to check if the stock's current price is 'below' the threshold_below value - this will indicate that the random forest ensemble is predicting that the stock price will go up by more than $5 in our prediction window.

    enter_crit_long = criteria.Position(symbol.close, 'below', threshold_below.value)

We also want to check if the current stock price is 'above' the threshold_above value, which would indicate that the random forest ensemble is predicting that the stock price will go down by more than $5 in our prediction window.

    enter_crit_short = criteria.Position(symbol.close, 'above', threshold_above.value)

As for our exit criteria, we only have one, and it would probably be wise if it matched our ensemble fitting parameters from earlier.  We fit the model to predict the price 5 days into the future.  Therefore, we should have an exit criteria that says, "When we've been in the market for 5 days, exit".

    exit_crit_long = criteria.TimeSinceAction(symbol, Long(), 5)
    exit_crit_short = criteria.TimeSinceAction(symbol, Short(), 5)

Pretty straightforward.  The TimeSinceAction criteria takes a stock, an action (such as Long(), Short(), LongExit(), ShortExit()), and a number of days/hours/minutes/etc.  The criteria will return true if the action specified has happened for the stock in the past X days/hours/minutes/etc -  In this case, if we have Long'ed and/or Short'ed GOOGL exactly 5 days ago.

We could have just as easily used +/- $5 from our stock price instead of the random forest prediction price. Then we could have checked if the random forest price fell outside that range to trade accordingly.

Now let's define what should happen when our criteria are met using criteria groups connected to market actions.
When our long entry criteria is true, we want to go long GOOGL.  When our short entry criteria is true, we want to short GOOGL.

    enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long], Long(), symbol)
    enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short], Short(), symbol)

Criteria groups take a list of criteria and will fire the action specified in their second parameter only if ALL criteria being checked end up being true for a particular point in time.  In this case, we've created a criteria group that will go ```Long()``` ```symbol```(GOOGL) when ```enter_crit_long``` is true, and go ```Short()``` ```symbol```(GOOGL) when ```enter_crit_short``` is true.

Now for our exit criteria groups:

    exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long], LongExit(), symbol)
    exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short], ShortExit(), symbol)

Let's create a trading profile for this simulation.  I'm thinking, $100,000 capital and for now we're just going to put down $10,000 per trade.  We're going to have $5 in trading fees.

    tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(5))

Well, we're just about ready to run this strategy!  Let's bring it all together:

    strat = strategy.Strategy(test_dataset, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2], tp)

The Strategy object simply takes our dataset (which now includes all of our technical indicators), a list of criteria groups (which handle checking for our criteria and performing the appropriate actions), and our trading profile.  You should never use your training dataset to test the performance of your random forest ensemble - use your testing dataset.

Let's run it!

    strat.simulate()
    print strat.report.pretty_overview()

If you installed the matplotlib python library, you can see some pretty charts with code along the lines of:

     fig = Figure(strat, rows=3) # Initialize a new figure with 3 rows
     fig.add_chart(googl, row=1) # Show candlesticks on chart 1
     fig.add_chart(googl.volume, row=2, plot_type='bar') # Show bar chart of GOOGL Volume on chart 2
     fig.add_capital_chart(row=3) # Show capital history on chart 3
     fig.show() # Display the figure

See the figures example [here](figures.md).

How did it do?  Add some data points, tweak some parameters, train for more iterations!```
