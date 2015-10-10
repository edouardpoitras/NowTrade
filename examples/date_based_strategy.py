import datetime
from nowtrade import symbol_list, data_connection, dataset, technical_indicator, \
                     criteria, criteria_group, trading_profile, trading_amount, \
                     trading_fee, strategy, action
dc = data_connection.YahooConnection()
sl = symbol_list.SymbolList(['^gspc']) # S&P 500
snp500 = sl.get('^gspc')
start = datetime.datetime(1980, 01, 01)
end = datetime.datetime(2015, 01, 01)
d = dataset.Dataset(sl, dc, start, end)
d.load_data()
# Go Long in November , Exit in May, every year.
enter_crit = criteria.IsMonth(11)
exit_crit = criteria.IsMonth(5)
enter_crit_group = criteria_group.CriteriaGroup([enter_crit], action.Long(), snp500)
exit_crit_group = criteria_group.CriteriaGroup([exit_crit], action.LongExit(), snp500)
tp = trading_profile.TradingProfile(100000, trading_amount.CapitalPercentage(100), trading_fee.StaticFee(20))
strat = strategy.Strategy(d, [enter_crit_group, exit_crit_group], tp)
strat.simulate()
print strat.report.pretty_overview()
