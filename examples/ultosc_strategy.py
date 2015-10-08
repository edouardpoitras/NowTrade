import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy, action

dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['GOOGL'])
symbol = sl.get('GOOGL')
print symbol
d = dataset.Dataset(sl, dc, datetime.datetime(2010, 01, 01), datetime.datetime(2015, 01, 01))
d.load_data()
ultosc = technical_indicator.ULTOSC(symbol, 14, 28, 56)
d.add_technical_indicator(ultosc)
# Enter Long
enter_crit_long1 = criteria.Below(ultosc.value, 40)
# Enter Short
enter_crit_short1 = criteria.Above(ultosc.value, 60)
# Exit Long
exit_crit_long1 = criteria.BarsSinceAction(symbol, action.Long(), 10)
# Exit Short
exit_crit_short1 = criteria.BarsSinceAction(symbol, action.Short(), 10)
# Criteria Groups
enter_crit_group1 = criteria_group.CriteriaGroup([enter_crit_long1], action.Long(), symbol)
enter_crit_group2 = criteria_group.CriteriaGroup([enter_crit_short1], action.Short(), symbol)
exit_crit_group1 = criteria_group.CriteriaGroup([exit_crit_long1], action.LongExit(), symbol)
exit_crit_group2 = criteria_group.CriteriaGroup([exit_crit_short1], action.ShortExit(), symbol)
# Strategy
tp = trading_profile.TradingProfile(11000, trading_amount.StaticAmount(10000), trading_fee.StaticFee(0))
strat = strategy.Strategy(d, [enter_crit_group1, enter_crit_group2, exit_crit_group1, exit_crit_group2], tp)
strat.simulate()
print strat.report.pretty_overview()
