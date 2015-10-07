import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy, figures
from nowtrade.action import Long, Short, LongExit, ShortExit

dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['AAPL'])
symbol = sl.get('AAPL')
start = datetime.datetime(2010, 01, 01)
end = datetime.datetime(2015, 01, 01)
d = dataset.Dataset(sl, dc, start, end)
d.load_data()
adx28 = technical_indicator.ADX(symbol, 28)
d.add_technical_indicator(adx28)
# Enter Long
enter_crit_long1 = criteria.Above(adx28.value, 30)
enter_crit_long2 = criteria.Above(adx28.minus_di, 30)
enter_crit_long3 = criteria.Below(adx28.plus_di, 20)
# Exit Long
exit_crit_long = criteria.BarsSinceLong(symbol, 10) # Exit 10 days later
# Criteria Groups
enter_crit_group = criteria_group.CriteriaGroup([enter_crit_long1, enter_crit_long2, enter_crit_long3], Long(), symbol)
exit_crit_group = criteria_group.CriteriaGroup([exit_crit_long], LongExit(), symbol)
# Strategy
tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(20000), trading_fee.StaticFee(10))
strat = strategy.Strategy(d, [enter_crit_group, exit_crit_group], tp)
strat.simulate()
print strat.report.pretty_overview()
