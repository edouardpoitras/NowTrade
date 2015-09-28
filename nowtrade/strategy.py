import time
import urllib2
import datetime
import uuid
import pandas as pd
import numpy as np
from nowtrade import logger
from nowtrade.action import LONG, SHORT, NO_ACTION, LONG_EXIT, SHORT_EXIT
from nowtrade import report

# In process_new_data, when iterating through cg_data, we get the warning defined here:
# http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
# This issue doesn't seem to affect our particular case.
# This warning is being surpressed with the following line:
pd.options.mode.chained_assignment = None

class Strategy:
    def __init__(self, dataset, criteria_groups, trading_profile, enter_on='Close', exit_on='Close'):
        self.dataset = dataset
        self.criteria_groups = criteria_groups
        self.trading_profile = trading_profile
        self.enter_on = enter_on
        self.exit_on = exit_on
        self.name = 'Strategy'
        self.report = report.Report(self, self.trading_profile)
        self.realtime_data_frame = pd.DataFrame() # Used for backtesting
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('Initialized - %s' %self)

    def __str__(self):
        return 'Strategy(dataset=%s, criteria_groups=%s, trading_profile=%s, enter_on=%s, exit_on=%s)' %(self.dataset, self.criteria_groups, self.trading_profile, self.enter_on, self.exit_on)
    def __repr__(self):
        return 'Strategy(dataset=%s, criteria_groups=%s, trading_profile=%s, enter_on=%s, exit_on=%s)' %(self.dataset, self.criteria_groups, self.trading_profile, self.enter_on, self.exit_on)

    def simulate(self, lookback_period=None):
        self.logger.info('Simulating strategy...')
        self.realtime_data_frame = pd.DataFrame()
        for row_data in self.dataset.data_frame.iterrows():
            data = row_data[1].to_frame().T
            self.process_new_data(data, lookback_period)

    def process_new_data(self, data, lookback_period=None):
        """
        Real-time trading method.
        Here we're assuming that data holds all the
        symbol data we'll need for the whole time slice.
        @type data: pandas.DataFrame
        @param data: Needs to have at least the OHLC for the
        new time slice of data.  There is no limit as to how
        many time slices of data can be contained in data.
        However, more data means more computationally
        intensive.
        @todo: This can be optimized by limiting the number
        of lookback for the TI/Criteria calculations.
        """
        self.logger.debug(data.index[-1])
        self.realtime_data_frame = self.realtime_data_frame.combine_first(data)
        # Process Standard Metrics
        for symbol in self.dataset.symbol_list:
            self.report.add_preprocess_metrics(str(symbol), self.realtime_data_frame)
        # Process criteria
        cg_data = {}
        for cg in self.criteria_groups:
            if cg.symbol not in cg_data: cg_data[cg.symbol] = []
            cg_result = cg.get_result(self.realtime_data_frame)
            cg_data[cg.symbol].append(cg_result)
        self.logger.debug('Criteria Group Data: %s' %cg_data)
        # Determine action based on all criteria group results
        for symbol in cg_data:
            symbol_action = self._determine_action(cg_data[symbol])
            self.logger.debug('%s: %s' %(symbol, symbol_action))
            # Keep track of market actions for each symbol
            self.realtime_data_frame['ACTIONS_%s' %symbol][-1] = symbol_action
            # Keep track of market position for each symbol
            self.realtime_data_frame['STATUS_%s' %symbol][-1] = self._get_status(symbol)
            # Update Report
            self.report.handle_action(symbol, self.realtime_data_frame)
        self.logger.debug('New data:\n%s' %self.realtime_data_frame.tail(1).to_string())

    def _determine_action(self, values):
        """
        Handles any conflicting actions based on multiple criteria groups.
        """
        # Can supply a pd.Series or a list
        try: values = values.values
        except: pass
        if LONG in values and SHORT in values: return NO_ACTION
        if LONG_EXIT in values and SHORT_EXIT in values: return NO_ACTION
        if LONG_EXIT in values: return LONG_EXIT
        if SHORT_EXIT in values: return SHORT_EXIT
        if LONG in values: return LONG
        if SHORT in values: return SHORT
        return NO_ACTION

    def _get_status(self, symbol):
        action = self.realtime_data_frame['ACTIONS_%s' %symbol][-1]
        # Replace SHORT with -1 and SHORT_EXIT with 1
        if action == SHORT: action = -1
        elif action == SHORT_EXIT: action = 1
        if len(self.realtime_data_frame) < 2: return action
        else: return self.realtime_data_frame['STATUS_%s' %symbol][-2] + action
