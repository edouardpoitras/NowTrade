import time, datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, report, strategy, ensemble
from nowtrade.action import Long, Short, LongExit, ShortExit

stocks = symbol_list.SymbolList(['GOOGL'])
symbol = stocks.get('GOOGL')
# We will train the random forest ensemble using 2 years of data
train_start = datetime.datetime(2013, 01, 01)
train_end = datetime.datetime(2015, 01, 01)
train_dataset = dataset.Dataset(stocks, data_connection.YahooConnection(), train_start, train_end)
train_dataset.load_data()
# Use the OHLCV data of the stock to predict the C in the future
rf = ensemble.Ensemble([symbol.open, symbol.high, symbol.low, symbol.close, symbol.volume], [symbol.close])
# Our ensemble will attempt to predict 5 bars in the future and will use 25 historical bars to do so
# number_of_jobs refers to the number of CPU threads to use when training
rf.build_ensemble(train_dataset, prediction_window=5, look_back_window=25, number_of_jobs=2)
# Let's start fitting the model
rf.fit()
# We can save our random forest ensemble for future use by using the save_to_file() function
rf.save_to_file('test.ens')
# This is how we would load it back up later
rf = ensemble.load_from_file('test.ens')
# Let's create our testing dataset
# It's important we don't test our network on the data it was trained with
test_start = datetime.datetime(2015, 01, 01)
test_end = datetime.datetime(2015, 07, 01)
test_dataset = dataset.Dataset(stocks, data_connection.YahooConnection(), test_start, test_end)
test_dataset.load_data()
# Technical Indicators
# We create the Ensemble technical indicator using the random forest created above
random_forest = technical_indicator.Ensemble(rf)
test_dataset.add_technical_indicator(random_forest)
# Our random forest will spit out a prediction price for 5 bars in the future
# We still need a threshold to determine whether or not we want to enter the trade
# Let's define a TI that is $5 higher than the random forest's prediction
threshold_above = technical_indicator.Addition(random_forest.value, 5)
test_dataset.add_technical_indicator(threshold_above)
# And $5 lower than the neural network's prediction
threshold_below = technical_indicator.Subtraction(random_forest.value, 5)
test_dataset.add_technical_indicator(threshold_below)
# Criteria
# Current price is below the threshold of our random forest's prediction price
enter_crit_long = criteria.Below(symbol.close, threshold_below.value)
# Current price is above the threshold of our random forest's prediction price
enter_crit_short = criteria.Above(symbol.close, threshold_above.value)
# Exit after 5 days - as per the random forest's build parameters
exit_crit_long = criteria.BarsSinceLong(symbol, 5)
exit_crit_short = criteria.BarsSinceShort(symbol, 5)
# Criteria Groups
enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long], Long(), symbol)
enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short], Short(), symbol)
exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long], LongExit(), symbol)
exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short], ShortExit(), symbol)
# Trading Profile
tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(5))
# Strategy
strat = strategy.Strategy(test_dataset, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2], tp)
strat.simulate()
print strat.report.pretty_overview()
