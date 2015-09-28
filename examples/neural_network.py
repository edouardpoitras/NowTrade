import time, datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, report, strategy, neural_network
from nowtrade.action import Long, Short, LongExit, ShortExit

dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['GOOGL'])
symbol = sl.get('GOOGL')
# Train the network using 5 years of data
train_start = datetime.datetime(2010, 01, 01)
train_end = datetime.datetime(2015, 01, 01)
train_dataset = dataset.Dataset(sl, dc, train_start, train_end)
train_dataset.load_data()
# Use the OHLCV data of the stock to predict the C in the future
nn = neural_network.NeuralNetwork([symbol.open, symbol.high, symbol.low, symbol.close, symbol.volume], [symbol.close])
# 3 hidden layers, 1 day prediction window for our close, learning rate of 0.001, momentum of 0.1
nn.build_network(train_dataset, hidden_layers=3, prediction_window=1, learning_rate=0.001, momentum=0.1)
# Let's train our network for 10 iterations
train_intervals = 10
for i in range(train_intervals): nn.train()
# We save the network to disk to be able to load it back up later
nn.save_to_file('test.nn')
# We can load the network using the following line of code
nn = neural_network.load_from_file('test.nn')
# Let's create our testing dataset
# It's important we don't test our network on the data it was trained with
test_start = train_end
test_end = datetime.datetime(2016, 01, 01)
test_dataset = dataset.Dataset(sl, dc, test_start, test_end)
test_dataset.load_data()
# Technical Indicators
# We create the NeuralNetwork technical indicator using the neural network trained above
neural_network = technical_indicator.NeuralNetwork(nn)
test_dataset.add_technical_indicator(neural_network)
# Our neural network will spit out a prediction price
# We still need a threshold to determine whether or not we want to enter the trade
# Let's define a TI that is $5 higher than the neural network's prediction
threshold_above = technical_indicator.Addition(neural_network.value, 5)
test_dataset.add_technical_indicator(threshold_above)
# And $5 lower than the neural network's prediction
threshold_below = technical_indicator.Subtraction(neural_network.value, 5)
test_dataset.add_technical_indicator(threshold_below)
# Criteria
# Current price is below the threshold of our neural network's prediction price
enter_crit_long = criteria.Position(symbol.close, 'below', threshold_below.value)
# Current price is above the threshold of our neural network's prediction price
enter_crit_short = criteria.Position(symbol.close, 'above', threshold_above.value)
# Exit after 1 day - as per the network's parameters
exit_crit_long = criteria.TimeSinceAction(symbol, Long(), 1)
exit_crit_short = criteria.TimeSinceAction(symbol, Short(), 1)
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
