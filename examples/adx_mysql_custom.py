"""
Slight modification on the ADX example that will use a MySQL DB and use a
custom column as a technical indicator.
"""
import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy
from nowtrade.action import Long, Short, LongExit, ShortExit

dc = data_connection.MySQLConnection(host='localhost',
                                     database='symbol_data',
                                     username='user',
                                     password='pass')
# Requires that your DB contains a table named after the symbol you want
# retrieve data from. Must also always be a capitalized table name.
# If you have a table called 'appl_data' which holds AAPL stock data, you will
# want to rename it to 'AAPL' like so:
# sql> RENAME TABLE appl_data TO AAPL;
# You also need columns named 'open', 'high', 'low', and 'close'.
# If you're using volume data, you need a column named 'volume'.
# All of this will be customizable in future versions of NowTrade.
sl = symbol_list.SymbolList(['AAPL'])
symbol = sl.get('AAPL')
start = datetime.datetime(2010, 01, 01)
end = datetime.datetime(2015, 01, 01)
d = dataset.Dataset(sl, dc, start, end)
# For MySQL, load_data can take many arguments.
# In this case, we don't care about volume data, we have a column named
# 'timestamp' which holds the date information, and we want to also pull in
# data from two custom columns named 'buyers' and 'sellers' (must be numeric).
d.load_data(volume=False, date_column='timestamp', custom_cols=['buyers', 'sellers'])
# ADX Technical Indicator.
adx28 = technical_indicator.ADX(symbol, 28)
d.add_technical_indicator(adx28)
# 10-day moving average based on one of our custom column.
buyers_sma = technical_indicator.SMA(stock.custom('buyers'), 10)
d.add_technical_indicator(buyers_sma)
# Enter Long
enter_crit_long1 = criteria.Above(adx28.value, 30)
enter_crit_long2 = criteria.Above(adx28.minus_di, 30)
enter_crit_long3 = criteria.Below(adx28.plus_di, 20)
enter_crit_long4 = criteria.Above(buyers_sma.value, 50000)
# Exit Long
exit_crit_long = criteria.BarsSinceLong(symbol, 10) # Exit 10 days later
# Criteria Groups
enter_crit_group = criteria_group.CriteriaGroup([enter_crit_long1, enter_crit_long2, enter_crit_long3, enter_crit_long4], Long(), symbol)
exit_crit_group = criteria_group.CriteriaGroup([exit_crit_long], LongExit(), symbol)
# Strategy
tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(20000), trading_fee.StaticFee(10))
strat = strategy.Strategy(d, [enter_crit_group, exit_crit_group], tp)
strat.simulate()
print strat.report.pretty_overview()
