import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy
from nowtrade.action import Long, Short, LongExit, ShortExit

dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['MSFT'])
symbol = sl.get('MSFT')
d = dataset.Dataset(sl, dc, datetime.datetime(2010, 01, 01), datetime.datetime(2015, 01, 01))
d.load_data()
rsi28 = technical_indicator.RSI(symbol.close, 28)
d.add_technical_indicator(rsi28)
sma100 = technical_indicator.SMA(symbol.close, 100)
d.add_technical_indicator(sma100)
sma100_previous = technical_indicator.Shift(sma100.value, 1)
d.add_technical_indicator(sma100_previous)
# Criteria
enter_crit_long1 = criteria.Above(rsi28.value, 60)
# SMA100 slope is moving up
enter_crit_long2 = criteria.Above(sma100.value, sma100_previous.value)
enter_crit_short1 = criteria.Below(rsi28.value, 40)
# SMA100 slope is moving down
enter_crit_short2 = criteria.Below(sma100.value, sma100_previous.value)
# Stop loss and take profit exit criteria
exit_crit_long1 = criteria.StopLoss(symbol, 0.01, percent=True) # 1%
exit_crit_long2 = criteria.TakeProfit(symbol, 50) # $100
exit_crit_short1 = criteria.StopLoss(symbol, 0.01, short=True, percent=True) # 1%
exit_crit_short2 = criteria.TakeProfit(symbol, 50, short=True) # $100
# Criteria Groups
enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long1, enter_crit_long2], Long(), symbol)
enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short1, enter_crit_short2], Short(), symbol)
exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long1], LongExit(), symbol)
exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_long2], LongExit(), symbol)
exit_crit_group3 = criteria_group.CriteriaGroup([exit_crit_short1], ShortExit(), symbol)
exit_crit_group4 = criteria_group.CriteriaGroup([exit_crit_short2], ShortExit(), symbol)
# Strategy
tp = trading_profile.TradingProfile(20000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(5))
strat = strategy.Strategy(d, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2, exit_crit_group3, exit_crit_group4], tp)
strat.simulate()
print strat.report.pretty_overview()
