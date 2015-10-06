"""
This module provides an abstraction layer over matplotlib's plotting
functionality.  It focuses on easily plotting charts of your strategy's
performance and technical indicators.
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ochl
from matplotlib.dates import date2num
from nowtrade import logger
from nowtrade import strategy
from nowtrade import symbol_list
from nowtrade.action import LONG, LONG_EXIT, SHORT, SHORT_EXIT

TI = 0 # Technical Indicator
TYPE = 1 # Chart type - line, bar, etc
COLOR = 2 # TI Color

class Figure(object): # pylint: disable=too-many-instance-attributes
    """
    @param dataset: A Dataset or Strategy object.
    """
    def __init__(self, dataset, rows=1, grid=True):
        # We need to handle a strategy being passed
        if isinstance(dataset, strategy.Strategy):
            self.strategy = dataset
            self.data_frame = self.strategy.dataset.data_frame
            self.realtime_data_frame = dataset.realtime_data_frame
        else: # Assume a dataset was passed
            self.strategy = None
            self.data_frame = dataset.data_frame
            self.realtime_data_frame = None
        self.data_frame.reset_index(inplace=True)
        date_conversion = lambda date: date2num(date.to_pydatetime())
        self.data_frame['DATE'] = self.data_frame['Date'].apply(date_conversion)
        self.rows = rows
        if grid:
            plt.rc('axes', grid=True)
            plt.rc('grid', color='0.75', linestyle='-', linewidth='0.2')
        self.current_figure = None
        self.figure_first_ax = None
        self.figure_rows = 1
        self.legend = []
        self.legend_labels = []
        self.add_figure(self.rows)
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('dataset: %s  rows: %s  grid: %s' %(dataset, rows, grid))

    def add_figure(self, rows=1):
        """
        This function adds a figure to the plotting instance.
        """
        self.figure_rows = rows
        self.current_figure = plt.figure()
        self.current_figure.subplots_adjust(hspace=0)
        self.figure_first_ax = None

    def add_chart(self, technical_indicator, row=1, plot_type='line', color='blue'):
        """
        This function adds a chart to the current figure.
        """
        axes = self.current_figure.add_subplot(self.figure_rows,
                                               1,
                                               row,
                                               sharex=self.figure_first_ax)
        if self.figure_first_ax is None:
            self.figure_first_ax = axes
        try:
            # Only works with ScalarFormatter
            axes.ticklabel_format(style='plain')
        except AttributeError:
            # Ignore on error
            pass
        if isinstance(technical_indicator, symbol_list.Symbol): # Candlesticks
            axes.set_title(str(technical_indicator))
            axes.set_ylabel('Price')
            cols = ['DATE',
                    technical_indicator.open,
                    technical_indicator.close,
                    technical_indicator.high,
                    technical_indicator.low]
            candlestick_ochl(axes, self.data_frame[cols].values, colorup=u'g')
            self.add_actions(technical_indicator, axes)
        else:
            if not isinstance(technical_indicator, str):
                # Probably forgot to submit the TI value
                technical_indicator = technical_indicator.value
            values = self.data_frame[str(technical_indicator)]
            axes.set_title(technical_indicator)
            axes.set_ylabel('Value')
            if plot_type == 'line':
                line, = axes.plot(self.data_frame['DATE'], values, color=color)
                self.legend.append(line)
            else:
                bars = axes.bar(self.data_frame['DATE'], values, color=color, width=0.3)
                self.legend.append(bars)
            self.legend_labels.append(technical_indicator)
        axes.xaxis_date()
        axes.autoscale_view()

    def add_capital_chart(self, row=1, color='green'):
        """
        This helper method will add a capital history chart to the current
        figure.
        """
        assert self.strategy is not None, \
            'You must initialize this figure with a strategy to use this functionality'
        axes = self.current_figure.add_subplot(self.figure_rows,
                                               1,
                                               row,
                                               sharex=self.figure_first_ax)
        if self.figure_first_ax is None:
            self.figure_first_ax = axes
        try:
            # Only works with ScalarFormatter
            axes.ticklabel_format(style='plain')
        except AttributeError:
            # Ignore on error
            pass
        axes.set_title('Capital')
        axes.set_ylabel('Money')
        capital_history = self.strategy.report.available_capital_history
        dates = pd.Series(capital_history.index).apply(lambda date: date2num(date.to_pydatetime()))
        values = capital_history.fillna(method='ffill')
        line, = axes.plot(dates, values, color=color)
        self.legend.append(line)
        self.legend_labels.append('Capital')
        axes.xaxis_date()
        axes.autoscale_view()

    def plot(self):
        """
        Actually does the plotting/displaying of the new figure.
        """
        plt.legend(self.legend, self.legend_labels, loc=0, shadow=True, fancybox=True)
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.setp([a.get_xticklabels() for a in self.current_figure.axes[:-1]], visible=False)
        #move_id = self.current_figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        plt.show()
    def show(self):
        """
        Alias to plot().
        """
        self.plot()

    def add_actions(self, symbol, axes):
        """
        This function will take care of adding all entry/exit actions on
        the candlestick chart.
        """
        actions_label = 'ACTIONS_%s' %symbol
        if self.realtime_data_frame is None or \
           actions_label not in self.realtime_data_frame.columns:
            return
        actions = self.realtime_data_frame[actions_label]
        actions = actions[actions != 0]
        for datetime, action in actions.iteritems():
            row = self.data_frame.loc[self.data_frame['Date'] == datetime]
            enter_value = row['%s_Open' %symbol]
            exit_value = row['%s_Open' %symbol]
            if action == LONG:
                axes.annotate('Long', xy=(datetime, enter_value),
                              xytext=(datetime, enter_value + 0.1),
                              arrowprops=dict(facecolor='green'))
            elif action == LONG_EXIT:
                axes.annotate('LongExit', xy=(datetime, exit_value),
                              xytext=(datetime, exit_value + 0.1),
                              arrowprops=dict(facecolor='green'))
            elif action == SHORT:
                axes.annotate('Short', xy=(datetime, enter_value),
                              xytext=(datetime, enter_value + 0.1),
                              arrowprops=dict(facecolor='red'))
            elif action == SHORT_EXIT:
                axes.annotate('ShortExit', xy=(datetime, exit_value),
                              xytext=(datetime, exit_value + 0.1),
                              arrowprops=dict(facecolor='red'))

    #def on_move(self, event):
        #"""
        #@todo: Speed up annotations.
        #"""
        #ax = event.inaxes
        #if ax is not None:
            #date_ordinal = round(event.xdata)
            #if date_ordinal == self.currentDateOrdinal: return
            #self.current_date_ordinal = date_ordinal
            #for ax in self.labels:
                #if date_ordinal in self.labels[ax]:
                    #self.textObjects[ax].set_text(self.labels[ax][dateOrdinal])
            #event.canvas.draw()
