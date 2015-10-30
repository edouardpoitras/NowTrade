# Neural Network Strategy Example

##### The user may want to educate themselves on potential issues with machine learning based strategies before using them in live trading, such as normalization of data, overfitting/underfitting, biases, etc. This is a very broad subject that is not cover here.

You can find the working source code of this strategy [here](neural_network.py).

_python imports have been omitted in this example, see the source code in the link above_

Let's create our stock list to inform our data connection which stocks to retrieve:

    stocks = StockList(['GOOGL'])

We need a way to reference the individual stock when we create our technical indicators and criteria:

    googl = stocks.get('GOOGL')

This way, we can access different stock values when defining our technical indicators and criteria, such as ```googl.open```, ```googl.close```, etc.  If this doesn't make sense just yet, don't worry, we'll cover technical indicators soon.

Let's specify our start and end dates for training our network.  It's important that our train and test data are different.  In this case, we will use 5 years of training data from 2010 to 2015, and 6 months of testing data from Jan 2015 to Jul 2015.

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

Alright, let's create our neural network.  We will Use the OHLCV data of the stock to predict the close price in the future.

    nn = neural_network.NeuralNetwork([googl.open, googl.high, googl.low, googl.close, googl.volume], [googl.close])

There we go!  This is also why we needed a reference to our googl stock from our stock list earlier.

We don't absolutely need to use the googl values to train our network.  We could also have used other stock values, indexes (if they were loaded in our dataset), technical indicators like RSI, SMA, or even other neural networks!  As long as the stock was in our StockList and we have a reference to the technical indicators that have been added to our dataset, we can utilize them in our data for training.

As an example, if we want to use the SMA technical indicator in our neural network training, we would have done the following:

    train_dataset = dataset.Dataset(stocks, YahooConnection(), train_start, train_end)
    train_dataset.load_data()
    sma_50 = SMA(googl.close, 50)
    train_dataset.add_technical_indicator(sma_50)
    nn = neural_network.NeuralNetwork([sma_50.value, googl.open, googl.high, googl.low, googl.close, googl.volume], [googl.close])

Cool.  For now, let's move forward with our original neural network we created.

_NOTE: for better results, you'll most likely want to normalize the data before feeding it to the neural network for training.  One way of accomplishing this is to use the ```PercentChange(ti)``` or ```Log(ti)``` technical indicators.  However, don't forget to account for this in your neural network's output.  If using percent change in your prediction values, the neural network will try to predict the percent change.  If using ```Log(ti)```, you'll need create another technical indicator using ```Exp(neural_network.value)``` to bring the values back to standard prices after prediction._

We're not quite done creating our network though.  We still need to configure it with all the nice bells and whistles that neural networks require. We're going to use a 1 day prediction window for our stock's close price, 3 hidden layers, a learning rate of 0.001, and momentum of 0.1. Typically, you will need to tweak these parameters quite a bit to find the right strategy for you.  For more help with these configuration options, see the PyBrain [documentation](http://pybrain.org/docs/) on neural networks.

    nn.build_network(train_dataset, hidden_layers=3, prediction_window=1, learning_rate=0.001, momentum=0.1)

Ahhh yes... training the network.  What fun!  For the sake of brevity we will be training our network for an entire 10 iterations.  The combination of the kind of data you provide it, your configurations above, and the number of training iterations performed, determines how successful your neural network will be at predicting the price.  However, I'm in no position to tell you what values to use for any of these.  Keep in mind that some traing models use thousands of training iterations and hundreds of data points.

    for i in range(10): nn.train()

You should see output on each iteration showing you what the current training error is.  It will look something like this:

    Total error: 0.941523156817
    Total error: 0.0291335258047
    Total error: 0.0288837959782
    Total error: 0.0287975948839
    Total error: 0.0287894245497
    Total error: 0.0286478173448
    Total error: 0.0286030342487
    Total error: 0.0284871828779
    Total error: 0.0283356715827
    Total error: 0.028049548077

As long as that number is going down, the network is improving!  However, be wary of overfitting.

We could have also tried ```nn.train_until_convergence()``` but that tends to take a while.

I recommend saving your neural network immediately after training for every strategy.  This way, if you stumble upon a really good one, you can load it up and use it for realtime trading.

    nn.save_to_file('test.nn')

We can load the network using the following line of code

  ~ nn = neural_network.load_from_file('test.nn')

Typically, this is the part where I would create the teating data set, but we've already done this above.  Let's attach our newly trained network to technical indicator so it can be used with our criteria.

    neural_network = technical_indicator.NeuralNetwork(nn, 'TestNN')
    test_dataset.add_technical_indicator(neural_network)

The 'TestNN' string parameter is optional.  It just makes the raw data easier to read (see below)

Our neural network will spit out prediction prices, but we still need a threshold to determine whether or not we want to enter the trade.
Let's define a technical indicator that is $5 higher than the neural network's prediction, and one that is $5 lower.

    threshold_above = technical_indicator.Addition(neural_network.value, 5)
    threshold_below = technical_indicator.Subtraction(neural_network.value, 5)

    test_dataset.add_technical_indicator(threshold_above)
    test_dataset.add_technical_indicator(threshold_below)

Now we can check if the neural network's prediction is $5 higher or lower than the current price, and take action!

Before we move on, it would be beneficial to see what the underlying pandas dataframe looks like:

    print test_dataset.data_frame.tail()

                GOOGL_Open  GOOGL_High   GOOGL_Low  GOOGL_Close  GOOGL_Volume  \
    Date
    2015-09-17  667.489990  681.989990  665.000000   671.669983       2356700
    2015-09-18  665.059998  669.840027  660.030029   660.919983       3592700
    2015-09-21  665.510010  669.000000  658.000000   666.979980       1907900
    2015-09-22  657.469971  658.820007  645.030029   653.200012       2700100
    2015-09-23  652.900024  660.280029  650.729980   653.289978       1454300

                GOOGL_Adj Close  \
    Date
    2015-09-17       671.669983
    2015-09-18       660.919983
    2015-09-21       666.979980
    2015-09-22       653.200012
    2015-09-23       653.289978

                NEURAL_NETWORK_TestNN \
    Date
    2015-09-17                                         652.601228
    2015-09-18                                         652.504164
    2015-09-21                                         652.629416
    2015-09-22                                         652.523667
    2015-09-23                                         652.643293

                ADDITION_NEURAL_NETWORK_TestNN_5 \
    Date
    2015-09-17                                         657.601228
    2015-09-18                                         657.504164
    2015-09-21                                         657.629416
    2015-09-22                                         657.523667
    2015-09-23                                         657.643293

                SUBTRACTION_NEURAL_NETWORK_TestNN_5
    Date
    2015-09-17                                         647.601228
    2015-09-18                                         647.504164
    2015-09-21                                         647.629416
    2015-09-22                                         647.523667
    2015-09-23                                         647.643293

Click [here](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) for more information on pandas dataframes.

And there you have it!  You can clearly see what the 'TestNN' predictions where on each day by looking at the ```NEURAL_NETWORK_TestNN``` column.  The ```ADDITION_NEURAL_NETWORK_TestNN_5``` and ```SUBTRACTION_NEURAL_NETWORK_TestNN_5``` are clearly +/- $5 from our 'TestNN' prediction values, and we can use those prices as our threshold to trading.

Let's create our trading criteria, starting with some entry criteria.  We want to check if the stock's current price is 'below' the threshold_below value - this will indicate that the neural network is predicting that the stock price will go up by more than $5 in our prediction window.

    enter_crit_long = criteria.Below(googl.close, threshold_below.value)

We also want to check if the current stock price is 'above' the threshold_above value, which would indicate that the neural network is predicting that the stock price will go down by more than $5 in our prediction window.

    enter_crit_short = criteria.Above(symbol.close, threshold_above.value)

As for our exit criteria, we only have one, and it would probably be wise if it matched our neural network training parameters from earlier.  We had trained the network to predict the price 1 day into the future.  Therefore, we should have an exit criteria that says, "When we've been in the market for 1 day(s), exit".

    exit_crit_long = criteria.BarsSinceLong(googl, 1)
    exit_crit_short = criteria.BarsSinceShort(googl, 1)

Pretty straightforward.  The BarsSinceLong/BarsSinceShort/BarsSinceLongExit/BarsSinceShortExit criteria takes a stock and a number of bars. The criteria will return true if the specific action has happened for the stock in the past X bars -  In this case, if we have Long'ed and/or Short'ed googl exactly 1 day ago.

We could have just as easily used +/- $5 from our stock price instead of the neural network prediction price. Then we could have checked if the neural network price fell outside that range to trade accordingly.

Now let's define what should happen when our criteria are met using criteria groups connected to market actions.
When our long entry criteria is true, we want to go long GOOGL.  When our short entry criteria is true, we want to short GOOGL.

    enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long], Long(), symbol)
    enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short], Short(), symbol)

Criteria groups take a list of criteria and will fire the action specified in their second parameter only if ALL criteria being checked end up being true in a particular point in time.  In this case, we've created a criteria group that will go ```Long()``` ```googl``` when ```enter_crit_long``` is true, and go ```Short()``` ```googl``` when ```enter_crit_short``` is true.

Now for our exit criteria groups:

    exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long], LongExit(), symbol)
    exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short], ShortExit(), symbol)

Let's create a trading profile for this simulation.  I'm thinking, $100,000 capital and for now we're just going to put down $10,000 per trade.  We're going to have $5 in trading fees.

    tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(5))

Well, we're just about ready to run this strategy!  Let's bring it all together:

    strat = strategy.Strategy(test_dataset, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2], tp)

The Strategy object simply takes our dataset (which now includes all of our technical indicators), a list of criteria groups (which handle checking for our criteria and performing the appropriate actions), and our trading profile.  You should always use your training dataset to test the performance of your neural network.

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

Once a strategy has run, we can do the following to see if the strategy calls for another trade on the upcoming bar:

    next_action = strategy.get_next_action()

If the ```next_action``` dictionary is not empty, we can examine it to determine what action to take in the market:

    action = next_action[googl]

    # One of 'LONG', 'SHORT', 'LONG_EXIT', 'SHORT_EXIT'
    print action['action_name']

    # Will always be 'OPEN' indicating to perform the action on the OPEN of the next bar
    print action['enter_on']

    # Uses the CLOSE of the current bar to estimate the price of the next OPEN
    print action['estimated_enter_value']

    # Uses the estimated_enter_value to determine the number of shares to buy/sell
    print action['estimated_shares'] # Based on your trading profile selected

    # Uses the estimaged_enter_value and estimaged_shares to determine the money required for the trade
    print action['estimated_money_required']

This information can be used during live trading.

How did it do?  Add some data points, tweak some parameters, train for more iterations!```
