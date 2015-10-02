import datetime
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.finance import candlestick, candlestick2, volume_overlay, volume_overlay2, volume_overlay3
from matplotlib.dates import date2num
from nowtrade import logger
from nowtrade import strategy
from nowtrade import symbol_list
from nowtrade.action import LONG, LONG_EXIT, SHORT, SHORT_EXIT

TI = 0 # Technical Indicator
TYPE = 1 # Chart type - line, bar, etc
COLOR = 2 # TI Color

class Figure():
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
        self.data_frame['DATE'] = self.data_frame['Date'].apply(lambda date: date2num(date.to_pydatetime()))
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

    def add_figure(self, rows=1):
        self.figure_rows = rows
        self.current_figure = plt.figure()
        self.current_figure.subplots_adjust(hspace=0)
        self.figure_first_ax = None

    def add_chart(self, ti, row=1, plot_type='line', color='blue'):
        ax = self.current_figure.add_subplot(self.figure_rows, 1, row, sharex=self.figure_first_ax)
        if self.figure_first_ax is None: self.figure_first_ax = ax
        try: ax.ticklabel_format(style='plain')
        except: pass
        if isinstance(ti, symbol_list.Symbol): # Candlesticks
            ax.set_title(str(ti))
            ax.set_ylabel('Price')
            csticks = candlestick(ax, self.data_frame[['DATE', ti.open, ti.close, ti.high, ti.low]].values, colorup=u'g')
            self.add_actions(ti, ax)
        else:
            if not isinstance(ti, str): ti = ti.value # Probably forgot to submit the TI value
            values = self.data_frame[str(ti)]
            ax.set_title(ti)
            ax.set_ylabel('Value')
            if plot_type == 'line':
                line, = ax.plot(self.data_frame['DATE'], values, color=color)
                self.legend.append(line)
            else:
                bar = ax.bar(self.data_frame['DATE'], values, color=color, width=0.3)
                self.legend.append(bar)
            self.legend_labels.append(ti)
        ax.xaxis_date()
        ax.autoscale_view()

    def add_capital_chart(self, row=1, color='green'):
        assert self.strategy is not None, 'You must initialize this figure with a strategy to use this functionality'
        ax = self.current_figure.add_subplot(self.figure_rows, 1, row, sharex=self.figure_first_ax)
        if self.figure_first_ax is None: self.figure_first_ax = ax
        try: ax.ticklabel_format(style='plain')
        except: pass
        ax.set_title('Capital')
        ax.set_ylabel('Money')
        capital_history = self.strategy.report.available_capital_history
        dates = pd.Series(capital_history.index).apply(lambda date: date2num(date.to_pydatetime()))
        values = capital_history.fillna(method='ffill')
        line, = ax.plot(dates, values, color=color)
        self.legend.append(line)
        self.legend_labels.append('Capital')
        ax.xaxis_date()
        ax.autoscale_view()

    def plot(self):
        plt.legend(self.legend, self.legend_labels, loc=0, shadow=True, fancybox=True)
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.setp([a.get_xticklabels() for a in self.current_figure.axes[:-1]], visible=False)
        #move_id = self.current_figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        plt.show()
    def show(self): self.plot()

    def add_actions(self, symbol, ax):
        actions_label = 'ACTIONS_%s' %symbol
        if self.realtime_data_frame is None or actions_label not in self.realtime_data_frame.columns: return
        actions = self.realtime_data_frame[actions_label]
        actions = actions[actions != 0]
        for dt, action in actions.iteritems():
            row = self.data_frame.loc[self.data_frame['Date'] == dt]
            enter_value = row['%s_Open' %symbol]
            exit_value = row['%s_Open' %symbol]
            if action == LONG:
                ax.annotate('Long', xy=(dt, enter_value),
                   xytext=(dt, enter_value + 0.1),
                   arrowprops=dict(facecolor='green'))
            elif action == LONG_EXIT:
                ax.annotate('LongExit', xy=(dt, exit_value),
                    xytext=(dt, exit_value + 0.1),
                    arrowprops=dict(facecolor='green'))
            elif action == SHORT:
                ax.annotate('Short', xy=(dt, enter_value),
                    xytext=(dt, enter_value + 0.1),
                    arrowprops=dict(facecolor='red'))
            elif action == SHORT_EXIT:
                ax.annotate('ShortExit', xy=(dt, exit_value),
                    xytext=(dt, exit_value + 0.1),
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
