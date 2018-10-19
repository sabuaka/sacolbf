# -*- coding: utf-8 -*-
'''test modle'''
from time import sleep
from matplotlib import pyplot as plt
import matplotlib.ticker as tick
import numpy as np

from sautility import shell
from sautility import dt
from sacolbf import SACollector as SACol
from sacolbf import SADataset as DS


class AnalysisGraph():
    ''''spred graph by matplotlib'''

    PRM_MAIN_PLOT_RANGE = 5000  # msec
    PRM_MAIN_PLOT_OFFSET = -500  # msec

    # [main:left]define for spread
    PRM_TICK_PRICE_TITLE = 'Tick price'
    PRM_TICK_PRICE_LINE_COLOR = '#DE9610'
    PRM_TICK_PRICE_LINE_WIDTH = 2.0

    PRM_TICK_ASK_TITLE = 'Tick Ask'
    PRM_TICK_ASK_LINE_COLOR = '#0074BF'
    PRM_TICK_ASK_LINE_WIDTH = 2.0

    PRM_TICK_BID_TITLE = 'Tick Bid'
    PRM_TICK_BID_LINE_COLOR = '#C93A40'
    PRM_TICK_BID_LINE_WIDTH = 2.0

    # [sub1:left]define for spread
    PRM_SPREAD_PRICE_TITLE = 'spread price'
    PRM_SPREAD_PRICE_LINE_COLOR = '#C93A40'
    PRM_SPREAD_PRICE_LINE_WIDTH = 2.0

    class PlotLines():
        '''Lines for plot'''
        tick_price = None
        tick_ask = None
        tick_bid = None
        ma_s5_diff = None
        spread_price = None

    def __init__(self):

        # create buffers to draw the graph
        self.buff_tick_price = np.empty((0, 2))
        self.buff_tick_bid = np.empty((0, 2))
        self.buff_tick_ask = np.empty((0, 2))

        self.buff_spread_price = np.empty((0, 2))

        # configure figure and plot
        plt.style.use('dark_background')

        self.fig = plt.figure(figsize=(14, 8))

        self.axes1_main = self.fig.add_axes((0.1, 0.3, 0.8, 0.6))
        self.axes2_main = self.fig.add_axes((0.1, 0.1, 0.8, 0.2), sharex=self.axes1_main)
        axes_list = [self.axes1_main, self.axes2_main]
        self.__configure_x_axis(axes_list)

        # create lines
        self.lines = self.PlotLines()

        # set axes1
        self.lines.tick_price, = self.axes1_main.plot(
            [], [],
            linewidth=self.PRM_TICK_PRICE_LINE_WIDTH,
            label=self.PRM_TICK_PRICE_TITLE,
            color=self.PRM_TICK_PRICE_LINE_COLOR
        )
        self.axes1_main.yaxis.grid(False)

        self.axes_tick_bid = self.axes1_main.twinx()
        self.lines.tick_bid, = self.axes_tick_bid.plot(
            [], [],
            linewidth=self.PRM_TICK_BID_LINE_WIDTH,
            label=self.PRM_TICK_BID_TITLE,
            color=self.PRM_TICK_BID_LINE_COLOR)
        self.axes_tick_bid.yaxis.grid(False)

        self.axes_tick_ask = self.axes1_main.twinx()
        self.lines.tick_ask, = self.axes_tick_ask.plot(
            [], [],
            linewidth=self.PRM_TICK_ASK_LINE_WIDTH,
            label=self.PRM_TICK_ASK_TITLE,
            color=self.PRM_TICK_ASK_LINE_COLOR)
        self.axes_tick_ask.yaxis.grid(False)

        lines_list = [self.lines.tick_price, self.lines.tick_ask, self.lines.tick_bid]
        label_list = [l.get_label() for l in lines_list]
        self.axes1_main.legend(lines_list, label_list, loc='upper left')

        # set axes2
        self.lines.spread_price, = self.axes2_main.plot(
            [], [],
            linewidth=self.PRM_SPREAD_PRICE_LINE_WIDTH,
            label=self.PRM_SPREAD_PRICE_TITLE,
            color=self.PRM_SPREAD_PRICE_LINE_COLOR)
        self.axes2_main.yaxis.grid(True)

        lines_list = [self.lines.spread_price]
        label_list = [l.get_label() for l in lines_list]
        self.axes2_main.legend(lines_list, label_list, loc='upper left')

    def __configure_x_axis(self, axes_list):

        for axes in axes_list:
            axes.xaxis.set_major_locator(tick.MultipleLocator(1000))
            axes.xaxis.set_minor_locator(tick.MultipleLocator(100))
            axes.grid(which='major', color='gray', linestyle='-')
            axes.grid(which='minor', color='gray', linestyle=':')
            if axes_list[-1] is axes:
                axes.tick_params(labelbottom=True)
            else:
                axes.tick_params(labelbottom=False)
            axes.xaxis.grid(True)

    def __update_buffer(self, target_buffer, x_data, y_data):

        # update graph data
        wbuff = np.append(target_buffer, np.array([[x_data, y_data]]), axis=0)

        # adjust the display range
        delete_limit = x_data - self.PRM_MAIN_PLOT_RANGE
        index = np.where(wbuff[:, 0] >= delete_limit)
        return wbuff[index]

    def update_tick(self, x_uts_ms, y_price, y_ask, y_bid):
        '''update data'''
        # create x axis data
        x_data = x_uts_ms

        # update graph data
        self.buff_tick_price = self.__update_buffer(
            self.buff_tick_price,
            int(x_data),
            float(y_price)
        )

        self.buff_tick_ask = self.__update_buffer(
            self.buff_tick_ask,
            int(x_data),
            float(y_ask)
        )

        self.buff_tick_bid = self.__update_buffer(
            self.buff_tick_bid,
            int(x_data),
            float(y_bid)
        )

    def update_spread(self, x_uts_ms, y_price):
        '''update data'''
        # create x axis data
        x_data = x_uts_ms

        # update graph data
        self.buff_spread_price = self.__update_buffer(
            self.buff_spread_price,
            int(x_data),
            float(y_price)
        )

    def draw(self, x_offset):
        '''draw graph'''
        self.__draw_fig_1_1(x_offset)
        self.__draw_fig_2_1(x_offset)

    def __draw_fig_1_1(self, x_offset):

        x_lim_min = self.PRM_MAIN_PLOT_RANGE
        x_lim_max = self.PRM_MAIN_PLOT_OFFSET

        buff_y = self.buff_tick_price[:, 1]
        if len(buff_y) <= 0:
            buff_y = [0]
        y_lim_min = min(buff_y) - 50
        y_lim_max = max(buff_y) + 50

        def set_buff_lines(lines, axis_buff, x_offset):
            '''set buffer to lines'''
            buff_x = abs(axis_buff[:, 0] - x_offset)
            buff_y = axis_buff[:, 1]
            lines.set_xdata(buff_x)
            lines.set_ydata(buff_y)

        set_buff_lines(self.lines.tick_price, self.buff_tick_price, x_offset)
        self.axes1_main.set_xlim(x_lim_min, x_lim_max)
        self.axes1_main.set_ylim(y_lim_min, y_lim_max)

        set_buff_lines(self.lines.tick_ask, self.buff_tick_ask, x_offset)
        self.axes_tick_ask.set_ylim(y_lim_min, y_lim_max)
        self.axes_tick_ask.set_yticks([], False)

        set_buff_lines(self.lines.tick_bid, self.buff_tick_bid, x_offset)
        self.axes_tick_bid.set_ylim(y_lim_min, y_lim_max)
        self.axes_tick_bid.set_yticks([], False)

    def __draw_fig_2_1(self, x_offset):

        buff_y = self.buff_spread_price[:, 1]
        y_lim_min = min(buff_y) - 5
        y_lim_max = max(buff_y) + 10

        buff_x_spread_price = abs(self.buff_spread_price[:, 0] - x_offset)
        buff_y_spread_price = self.buff_spread_price[:, 1]
        self.axes2_main.set_ylim(y_lim_min, y_lim_max)
        self.lines.spread_price.set_xdata(buff_x_spread_price)
        self.lines.spread_price.set_ydata(buff_y_spread_price)


class MainProc():
    '''class for main proc'''

    def __init__(self):
        self.graph = AnalysisGraph()

    def on_event(self, evt, ds: DS):  # Fixed I/F pylint: disable-msg=W0613
        '''event proceduer for callback'''
        try:
            if not ds.dsc_tick_fx.is_available():
                return

            if evt == SACol.UpdateEvent.TICK:
                uts_ms_now = dt.get_uts_ms()

                self.graph.update_tick(
                    uts_ms_now,
                    ds.dsc_tick_fx.trade_price,
                    ds.dsc_tick_fx.ask_price,
                    ds.dsc_tick_fx.bid_price)

                self.graph.update_spread(
                    uts_ms_now,
                    ds.dsc_tick_fx.spread
                )

                self.graph.draw(uts_ms_now)

            shell.clear()
            print('tick: price', ds.dsc_tick_fx.trade_price)
            print('tick: bid', ds.dsc_tick_fx.bid_price)
            print('tick: ask', ds.dsc_tick_fx.ask_price)

        except:
            import traceback
            with open('error.log', 'a') as f:
                f.write(dt.get_dt_long() + '\n')
                traceback.print_exc(file=f)

if __name__ == '__main__':
    main_proc = MainProc()
    col = SACol(event_callback=main_proc.on_event)
    print('request to col start')
    col.start()
    print('col start is completed')
    while True:
        try:
            key = shell.nb_getch()
            if key == b'q':
                print('request col stop')
                col.stop()
                print('col stop is completed')
                break
            sleep(0.01)
            plt.pause(0.01)
        except KeyboardInterrupt:
            col.stop()
            break

    print('normal finish app')
