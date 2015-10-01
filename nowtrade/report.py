import pandas as pd
import numpy as np
from nowtrade import logger
from nowtrade.trade import Trade
from nowtrade.action import LONG, LONG_EXIT, SHORT, SHORT_EXIT, NO_ACTION

class Report:
    def __init__(self, strategy, trading_profile):
        self.strategy = strategy
        self.trading_profile = trading_profile
        self._reset()
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('strategy: %s  trading_profile: %s' %(strategy, trading_profile))

    def _reset(self):
        self.trade_history = {}
        self.available_money = self.trading_profile.capital
        self.capital = self.trading_profile.capital
        self.available_money_history = pd.Series(index=self.strategy.dataset.data_frame.index)
        self.available_capital_history = pd.Series(index=self.strategy.dataset.data_frame.index)
        self.ongoing_trades = {}
        self.trades = 0
        self.average_gain = 0.0
        self.sharpe_ratio = 0.0
        self.average_trading_amount = 0.0
        self.average_bars = 0.0
        self.total_fees = 0.0
        self.average_fees = 0.0
        self.total_slippage = 0.0
        self.average_slippage = 0.0
        self.winning_trades = 0
        self.losing_trades = 0
        self.average_winning_gain = 0.0
        self.average_losing_gain = 0.0
        self.percent_profitable = 0.0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        self.net_profit = 0.0
        self.lacking_capital = 0
        self._require_finalize_calculations = False

    def add_preprocess_metrics(self, symbol, data_frame):
        """
        Adds required metrics for certain criteria that can't be easily added
        as technical indicators.  IE: P/L, ACTIONS, STATUS, etc
        This only updates the last data entry.
        """
        if symbol not in self.ongoing_trades:
            self.ongoing_trades[symbol] = None
        if 'PL_%s' %symbol not in data_frame:
            data_frame['PL_%s' %symbol] = pd.Series(index=data_frame.index)
        if 'PL_VALUE_%s' %symbol not in data_frame:
            data_frame['PL_VALUE_%s' %symbol] = pd.Series(index=data_frame.index)
        if 'PL_PERCENT_%s' %symbol not in data_frame:
            data_frame['PL_PERCENT_%s' %symbol] = pd.Series(index=data_frame.index)
        trade = self.ongoing_trades[symbol]
        status = data_frame['STATUS_%s' %symbol][-1]
        action = data_frame['ACTIONS_%s' %symbol][-1]
        open_value = data_frame['%s_Open' %symbol][-1]
        close_value = data_frame['%s_Close' %symbol][-1]
        change = close_value - open_value
        exiting = action == LONG_EXIT or action == SHORT_EXIT
        if trade and exiting: # Exiting Ongoing Trade
            enter_change = open_value - trade.price
            percent_change = enter_change / trade.price
            pl = percent_change * trade.money
            if status < 0: # Shorting
                pl = pl * -1
            data_frame['PL_%s' %symbol][-1] = pl
            data_frame['PL_VALUE_%s' %symbol][-1] = enter_change
            data_frame['PL_PERCENT_%s' %symbol][-1] = percent_change
        elif trade: # Ongoing Trade
            enter_close_value = data_frame['%s_Close' %symbol][trade.datetime]
            enter_change = close_value - trade.price
            percent_change = enter_change / trade.price
            pl = percent_change * trade.money
            if status < 0: # Shorting
                pl = pl * -1
            data_frame['PL_%s' %symbol][-1] = pl
            data_frame['PL_VALUE_%s' %symbol][-1] = enter_change
            data_frame['PL_PERCENT_%s' %symbol][-1] = percent_change
        elif data_frame['ACTIONS_%s' %symbol][-1] != 0: # New Enter/Exit Trade
            shares = self.trading_profile.trading_amount.get_shares(open_value, self.available_money)
            fee = self.trading_profile.trading_fee.get_fee(open_value, shares)
            money = open_value * shares
            pl = shares * close_value - money
            percent_change = pl / money
            if status < 0: # Shorting
                pl = pl * -1
            data_frame['PL_%s' %symbol][-1] = pl
            data_frame['PL_VALUE_%s' %symbol][-1] = change
            data_frame['PL_PERCENT_%s' %symbol][-1] = percent_change
        else: # Not in trade
            data_frame['PL_%s' %symbol][-1] = np.nan
            data_frame['PL_VALUE_%s' %symbol][-1] = np.nan
            data_frame['PL_PERCENT_%s' %symbol][-1] = np.nan
        self._require_finalize_calculations = True

    def handle_action(self, symbol, data_frame):
        datetime = data_frame.index[-1]
        data = data_frame.iloc[-1]
        action = data['ACTIONS_%s' %symbol]
        if action == LONG: self.long(data, datetime, symbol)
        elif action == SHORT: self.short(data, datetime, symbol)
        elif action == LONG_EXIT: self.long_exit(data, datetime, symbol)
        elif action == SHORT_EXIT: self.short_exit(data, datetime, symbol)

    def long(self, data, datetime, symbol):
        price = data['%s_Open' %symbol]
        shares = self.trading_profile.trading_amount.get_shares(price, self.available_money)
        fee = self.trading_profile.trading_fee.get_fee(price, shares)
        money = price * shares
        slippage = money * self.trading_profile.slippage / 100
        self.total_fees += fee
        self.total_slippage += slippage
        self.average_trading_amount += money
        self.available_money -= (money + fee + slippage)
        trade = Trade(datetime, 'LONG', symbol, price, shares, money, fee, slippage)
        self.ongoing_trades[symbol] = trade
        if symbol not in self.trade_history: self.trade_history[symbol] = []
        self.trade_history[symbol].append(Trade(datetime, 'LONG', symbol, price, shares, money, fee, slippage))
        self.available_money_history[datetime] = self.available_money
        self.available_capital_history[datetime] = self.capital

    def short(self, data, datetime, symbol):
        price = data['%s_Open' %symbol]
        shares = self.trading_profile.trading_amount.get_shares(price, self.available_money)
        fee = self.trading_profile.trading_fee.get_fee(price, shares)
        money = price * shares
        slippage = money * self.trading_profile.slippage / 100
        self.total_fees += fee
        self.total_slippage += slippage
        self.average_trading_amount += money
        self.available_money -= (money + fee + slippage)
        self.ongoing_trades[symbol] = Trade(datetime, 'SHORT', symbol, price, shares, money, fee, slippage)
        if symbol not in self.trade_history: self.trade_history[symbol] = []
        self.trade_history[symbol].append(Trade(datetime, 'SHORT', symbol, price, shares, money, fee, slippage))
        self.available_money_history[datetime] = self.available_money
        self.available_capital_history[datetime] = self.capital

    def long_exit(self, data, datetime, symbol):
        if not self.ongoing_trades[symbol]:
            print 'Could not simulate LongExit for %s on %s, no corresponding action' %(symbol, datetime)
            return
        trade = self.ongoing_trades[symbol]
        self.ongoing_trades[symbol] = None
        price = data['%s_Open' %symbol]
        fee = self.trading_profile.trading_fee.get_fee(price, trade.shares)
        money = price * trade.shares
        slippage = money * self.trading_profile.slippage / 100
        self.total_fees += fee
        self.total_slippage += slippage
        profit_loss = money - trade.money # Made this much off the trade
        profit_loss -= trade.fee # Minus Fees In
        profit_loss -= fee # Minus Fees Out
        profit_loss -= trade.slippage # Minus Slippage In
        profit_loss -= slippage # Minus Slippage Out
        self.available_money += (money - fee - slippage)
        gains = profit_loss / (money - fee - slippage)
        self.average_gain += gains
        self.capital += profit_loss
        self.trade_history[symbol].append(Trade(datetime, 'LONG_EXIT', symbol, price, trade.shares, money, fee, slippage))
        self.available_money_history[datetime] = self.available_money
        self.available_capital_history[datetime] = self.capital
        if gains > 0:
            self.winning_trades += 1
            self.average_winning_gain += gains
            self.gross_profit += profit_loss
        else:
            self.losing_trades += 1
            self.average_losing_gain += gains
            self.gross_loss += profit_loss
        self.trades += 1

    def short_exit(self, data, datetime, symbol):
        if not self.ongoing_trades[symbol]:
            print 'Did not simulate LongExit for %s on %s - probably not enough capital' %(symbol, datetime)
            return
        trade = self.ongoing_trades[symbol]
        self.ongoing_trades[symbol] = None
        price = data['%s_Open' %symbol]
        fee = self.trading_profile.trading_fee.get_fee(price, trade.shares)
        money = price * trade.shares
        slippage = money * self.trading_profile.slippage / 100
        self.total_fees += fee
        self.total_slippage += slippage
        profit_loss = trade.money - money # Made this much off the trade
        profit_loss -= trade.fee # Minus Fees In
        profit_loss -= fee # Minus Fees Out
        profit_loss -= trade.slippage # Minus Slippage In
        profit_loss -= slippage # Minus Slippage Out
        self.available_money += (money - fee - slippage)
        gains = profit_loss / (money - fee - slippage)
        self.average_gain += gains
        self.capital += profit_loss
        self.trade_history[symbol].append(Trade(datetime, 'SHORT_EXIT', symbol, price, trade.shares, money, fee, slippage))
        self.available_money_history[datetime] = self.available_money
        self.available_capital_history[datetime] = self.capital
        if gains > 0:
            self.winning_trades += 1
            self.average_winning_gain += gains
            self.gross_profit += profit_loss
        else:
            self.losing_trades += 1
            self.average_losing_gain += gains
            self.gross_loss += profit_loss
        self.trades += 1

    def finalize_calculations(self):
        if self.trades == 0: return # No trades for this time period
        self.average_gain = self.average_gain / self.trades
        self.average_trading_amount = self.average_trading_amount / self.trades
        self.average_fees = self.total_fees / self.trades
        self.average_slippage = self.total_slippage / self.trades
        if self.winning_trades != 0:
            self.average_winning_gain = self.average_winning_gain / self.winning_trades
        if self.losing_trades != 0:
            self.average_losing_gain = self.average_losing_gain / self.losing_trades
        self.percent_profitable = self.winning_trades * 1.0 / self.trades * 100
        self.net_profit = self.gross_profit + self.gross_loss
        # Capital history should start at trading_profile.capital, not at nan/0
        if np.isnan(self.available_capital_history[0]): self.available_capital_history[0] = self.trading_profile.capital
        self.available_capital_history = self.available_capital_history.fillna(method='ffill')
        self.sharpe_ratio = self.get_sharpe_ratio()
        self._require_finalize_calculations = False

    def get_sharpe_ratio(self, periods=252, benchmark=None):
        """
        Benchmark can be an int representing the annualized return (5 for 5%)
        or another time series.
        """
        returns = self.available_capital_history.pct_change()
        if benchmark == None:
            return np.sqrt(periods) * returns.mean() / returns.std()
        elif type(benchmark) in (int, float, long):
            excess_returns = returns - 0.05/periods
            return np.sqrt(periods) * excess_returns.mean() / excess_returns.std()
        else: # Assume a Series for the benchmark
            bench_returns = benchmark.pct_change()
            excess_returns = returns - bench_returns
            return np.sqrt(periods) * excess_returns.mean() / excess_returns.std()

    def get_average_bars(self):
        bars = 0.0
        for symbol in self.trade_history:
            last_trade = None
            for trade in self.trade_history[symbol]:
                if trade.action == 'SHORT_EXIT' or trade.action == 'LONG_EXIT':
                    bars += len(self.strategy.dataset.data_frame[last_trade.datetime:trade.datetime])
                    last_trade = None
                else: last_trade = trade
        return bars / self.trades

    def overview(self):
        if self._require_finalize_calculations: self.finalize_calculations()
        overview = {}
        if self.trades > 0:
            overview['average_trading_amount'] = self.average_trading_amount
            overview['average_fees'] = self.average_fees
            overview['average_slippage'] = self.average_slippage
            overview['average_gains'] = self.average_gain*100
            overview['average_winner'] = self.average_winning_gain*100
            overview['average_loser'] = self.average_losing_gain*100
            overview['average_bars'] = self.get_average_bars()
            overview['profitability'] = self.percent_profitable
            overview['gross_profit'] = self.gross_profit
            overview['gross_loss'] = self.gross_loss
            overview['net_profit'] = self.net_profit
            overview['winning_trades'] = self.winning_trades
            overview['losing_trades'] = self.losing_trades
            overview['sharpe_ratio'] = self.sharpe_ratio
        overview['total_fees'] = self.total_fees
        overview['total_slippage'] = self.total_slippage
        overview['trades'] = self.trades
        overview['lacking_capital'] = self.lacking_capital
        overview['ongoing_trades'] = len([symbol for symbol in self.ongoing_trades if self.ongoing_trades[symbol]])
        overview['trade_history'] = self.trade_history
        overview['available_money_history'] = self.available_money_history
        overview['available_capital_history'] = self.available_capital_history
        return overview

    def pretty_overview(self):
        overview = self.overview()
        if overview['trades'] == 0:
            ret = 'No trades\n'
            ret += 'Ongoing Trades: %s\n' %overview['ongoing_trades']
            ret += 'Trades Lacking Capital: %s' %overview['lacking_capital']
            return ret
        ret = 'Trades:\n'
        for symbol in overview['trade_history']:
            ret += '%s\n' %symbol
            for trade in overview['trade_history'][symbol]:
                ret += '%s\n' %str(trade)
        ret += 'Profitability: %s\n' %overview['profitability']
        ret += '# Trades: %s\n' %overview['trades']
        ret += 'Net Profit: %s\n' %overview['net_profit']
        ret += 'Gross Profit: %s\n' %overview['gross_profit']
        ret += 'Gross Loss: %s\n' %overview['gross_loss']
        ret += 'Winning Trades: %s\n' %overview['winning_trades']
        ret += 'Losing Trades: %s\n' %overview['losing_trades']
        ret += 'Sharpe Ratio: %s\n' %overview['sharpe_ratio']
        ret += 'Avg. Trading Amount: %s\n' %overview['average_trading_amount']
        ret += 'Avg. Fees: %s\n' %overview['average_fees']
        ret += 'Avg. Slippage: %s\n' %overview['average_slippage']
        ret += 'Avg. Gains: %s\n' %overview['average_gains']
        ret += 'Avg. Winner: %s\n' %overview['average_winner']
        ret += 'Avg. Loser: %s\n' %overview['average_loser']
        ret += 'Avg. Bars: %s\n' %overview['average_bars']
        ret += 'Total Fees: %s\n' %overview['total_fees']
        ret += 'Total Slippage: %s\n' %overview['total_slippage']
        ret += 'Trades Lacking Capital: %s\n' %overview['lacking_capital']
        ret += 'Ongoing Trades: %s' %overview['ongoing_trades']
        return ret
