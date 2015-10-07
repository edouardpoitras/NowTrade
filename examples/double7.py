import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy
from nowtrade.action import Long, Short, LongExit, ShortExit

dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['GOOGL'])
symbol = sl.get('GOOGL')
start = datetime.datetime(2010, 01, 01)
end = datetime.datetime(2015, 01, 01)
d = dataset.Dataset(sl, dc, start, end)
d.load_data()
sma100 = technical_indicator.SMA(symbol.close, 100)
d.add_technical_indicator(sma100)
high7 = technical_indicator.Max(symbol.close, 7)
d.add_technical_indicator(high7)
low7 = technical_indicator.Min(symbol.close, 7)
d.add_technical_indicator(low7)
# Enter Long
enter_crit_long1 = criteria.Above(symbol.close, sma100.value)
enter_crit_long2 = criteria.Equals(symbol.close, low7.value)
enter_crit_short1 = criteria.Below(symbol.close, sma100.value)
enter_crit_short2 = criteria.Equals(symbol.close, high7.value)
# Exit Long
exit_crit_long1 = criteria.StopLoss(symbol, 5)
exit_crit_long2 = criteria.TakeProfit(symbol, 10)
exit_crit_short1 = criteria.StopLoss(symbol, 5)
exit_crit_short2 = criteria.TakeProfit(symbol, 10)
# Criteria Groups
enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long1, enter_crit_long2], Long(), symbol)
enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short1, enter_crit_short2], Short(), symbol)
exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long1], LongExit(), symbol)
exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_long2], LongExit(), symbol)
exit_crit_group3 = criteria_group.CriteriaGroup([exit_crit_short1], ShortExit(), symbol)
exit_crit_group4 = criteria_group.CriteriaGroup([exit_crit_short2], ShortExit(), symbol)
# Strategy
tp = trading_profile.TradingProfile(100000, trading_amount.StaticAmount(20000), trading_fee.StaticFee(10))
strat = strategy.Strategy(d, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2, exit_crit_group3, exit_crit_group4], tp)
strat.simulate()
print strat.report.pretty_overview()
