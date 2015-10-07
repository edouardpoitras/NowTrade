import datetime
from nowtrade.symbol_list import StockList
from nowtrade.data_connection import YahooConnection
from nowtrade.dataset import Dataset
from nowtrade.technical_indicator import SMA
from nowtrade.criteria import CrossingAbove, TrailingStop
from nowtrade.criteria_group import CriteriaGroup
from nowtrade.action import Long, LongExit
from nowtrade.trading_profile import TradingProfile
from nowtrade.trading_amount import StaticAmount
from nowtrade.trading_fee import StaticFee
from nowtrade.strategy import Strategy

# Create our stock list to inform our data connection which stocks to retrieve
stocks = StockList(['GOOGL'])
# We can now use this variable to reference our stock when defining enter/exit criteria
googl = stocks.get('GOOGL')
# Specify our start and end dates for this backtest
start = datetime.datetime(2010, 01, 01)
end = datetime.datetime(2015, 01, 01)
# Create the dataset that will hold all of the stock data
stock_data = Dataset(stocks, YahooConnection(), start, end)
# Loading data now before running the strategy allows us to resample the data if needed
stock_data.load_data()
# Create our technical indicators
# 50-day simple moving average of GOOGL close prices
sma50 = SMA(googl.close, 50)
# 100-day simple moving average of GOOGL close prices
sma100 = SMA(googl.close, 100)
# Now that we've defined our technical indicators, we need to apply them to our dataset
stock_data.add_technical_indicator(sma50)
stock_data.add_technical_indicator(sma100)
# Let's define our entry/exit criteria
# Enter long position when the 50-day moving average crosses over the 100-day moving average
enter_crit_long = CrossingAbove(sma50, sma100)
# Our exit criteria will simply be a trailing stop of 5%
exit_crit_long = TrailingStop(googl, 0.05, percent=True)
# Now let's define what should happen when our criteria are met using criteria groups
# When our two entry criteria are active, we want to go long GOOGL
enter_crit_group = CriteriaGroup([enter_crit_long], Long(), googl)
# When our exit criteria is active, we want to exit our long position with GOOGL
exit_crit_group = CriteriaGroup([exit_crit_long], LongExit(), googl)
# We need to create a trading profile before running our backtest
# Starting capital of $100,000, $10,000/trade, fees of $10/trade
profile = TradingProfile(100000, StaticAmount(10000), StaticFee(10))
# Let's ready our strategy - specifying the dataset, criteria groups, and trading profile
strategy = Strategy(stock_data, [enter_crit_group, exit_crit_group], profile)
# Run the backtest
strategy.simulate()
print strategy.report.pretty_overview()
