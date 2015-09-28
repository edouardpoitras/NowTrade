import datetime
from nowtrade.symbol_list import StockList
from nowtrade.data_connection import YahooConnection
from nowtrade.dataset import Dataset
from nowtrade.technical_indicator import SMA
from nowtrade.criteria import Crossing, TrailingStop
from nowtrade.criteria_group import CriteriaGroup
from nowtrade.action import Long, LongExit
from nowtrade.trading_profile import TradingProfile
from nowtrade.trading_amount import StaticAmount
from nowtrade.trading_fee import StaticFee
from nowtrade.report import Report
from nowtrade.strategy import Strategy
from nowtrade.figures import Figure

# This is a standard crossover strategy that we won't get into here
stocks = StockList(['GOOGL'])
googl = stocks.get('GOOGL')
start = datetime.datetime(2013, 01, 01)
end = datetime.datetime(2015, 01, 01)
stock_data = Dataset(stocks, YahooConnection(), start, end)
stock_data.load_data()
sma10 = SMA(googl.close, 10)
sma25 = SMA(googl.close, 25)
stock_data.add_technical_indicator(sma10)
stock_data.add_technical_indicator(sma25)
enter_crit_long = Crossing(sma10.value, 'above', sma25.value)
exit_crit_long = TrailingStop(googl, 0.05, percent=True)
enter_crit_group = CriteriaGroup([enter_crit_long], Long(), googl)
exit_crit_group = CriteriaGroup([exit_crit_long], LongExit(), googl)
profile = TradingProfile(100000, StaticAmount(10000), StaticFee(5))
strategy = Strategy(stock_data, [enter_crit_group, exit_crit_group], profile)
strategy.simulate()
# Show some charts
fig = Figure(strategy, rows=4) # 4 charts in this figure
# Note that Figure() can be initialized with a dataset instead of a strategy object.
# In that case you would not see the enter/exits in the candlestick chart
# and you would not have access to the add_capital_chart() function.
fig.add_chart(googl, 1) # First chart holds the googl candlesticks
fig.add_chart(googl.volume, 2, 'bar') # Second chart holds the volume
fig.add_chart(sma10, 3) # Third chart holds the simple moving averages
fig.add_chart(sma25, 3, color='red') # SMA25 will have a red line
fig.add_capital_chart(4) # Show the capital history on the last chart
fig.show() # Show the figure
