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

# pylint: disable-msg=C0103,C1801,R0201,R0902,R0903,W0702


class AnalysisGraph():
    ''''spred graph by matplotlib'''

    PRM_MAIN_PLOT_RANGE = 8000  # msec
    PRM_MAIN_PLOT_OFFSET = -500  # msec

    # [axes1] define for tick
    PRM_TICK_PRICE_TITLE = 'tick price'
    PRM_TICK_PRICE_LINE_COLOR = '#DE9610'
    PRM_TICK_PRICE_LINE_WIDTH = 2.0

    PRM_TICK_ASK_TITLE = 'tick ask'
    PRM_TICK_ASK_LINE_COLOR = '#0074BF'
    PRM_TICK_ASK_LINE_WIDTH = 2.0

    PRM_TICK_BID_TITLE = 'tick bid'
    PRM_TICK_BID_LINE_COLOR = '#C93A40'
    PRM_TICK_BID_LINE_WIDTH = 2.0

    # [axes2] define for spread
    PRM_SPREAD_PRICE_TITLE = 'spread price'
    PRM_SPREAD_PRICE_LINE_COLOR = '#C93A40'
    PRM_SPREAD_PRICE_LINE_WIDTH = 2.0

    # [axes3] define for depth by tick data
    PRM_TICK_TOTAL_ASK_TITLE = 'tick total ask'
    PRM_TICK_TOTAL_ASK_LINE_COLOR = '#0074BF'
    PRM_TICK_TOTAL_ASK_LINE_WIDTH = 2.0

    PRM_TICK_TOTAL_BID_TITLE = 'tick total bid'
    PRM_TICK_TOTAL_BID_LINE_COLOR = '#C93A40'
    PRM_TICK_TOTAL_BID_LINE_WIDTH = 2.0

    class PlotLines():
        '''Lines for plot'''
        tick_price = None
        tick_ask = None
        tick_bid = None
        spread_price = None
        total_bid_amount = None
        total_ask_amount = None

    def __init__(self):

        # create buffers to draw the graph
        self.buff_tick_price = np.empty((0, 2))
        self.buff_tick_bid = np.empty((0, 2))
        self.buff_tick_ask = np.empty((0, 2))

        self.buff_spread_price = np.empty((0, 2))

        self.buff_total_bid_amount = np.empty((0, 2))
        self.buff_total_ask_amount = np.empty((0, 2))

        # configure figure and plot
        plt.style.use('dark_background')

        self.fig = plt.figure(figsize=(14, 8))

        self.axes1_main = self.fig.add_axes((0.1, 0.5, 0.8, 0.4))
        self.axes2_main = self.fig.add_axes((0.1, 0.3, 0.8, 0.2), sharex=self.axes1_main)
        self.axes3_main = self.fig.add_axes((0.1, 0.1, 0.8, 0.2), sharex=self.axes1_main)
        axes_list = [self.axes1_main, self.axes2_main, self.axes3_main]
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

        # set axes3
        self.lines.total_bid_amount, = self.axes3_main.plot(
            [], [],
            linewidth=self.PRM_TICK_TOTAL_BID_LINE_WIDTH,
            label=self.PRM_TICK_TOTAL_BID_TITLE,
            color=self.PRM_TICK_TOTAL_BID_LINE_COLOR)
        self.axes3_main.yaxis.grid(True)

        self.axes_total_ask_amount = self.axes3_main.twinx()
        self.lines.total_ask_amount, = self.axes_total_ask_amount.plot(
            [], [],
            linewidth=self.PRM_TICK_TOTAL_ASK_LINE_WIDTH,
            label=self.PRM_TICK_TOTAL_ASK_TITLE,
            color=self.PRM_TICK_TOTAL_ASK_LINE_COLOR)
        self.axes_total_ask_amount.yaxis.grid(False)

        lines_list = [self.lines.total_bid_amount, self.lines.total_ask_amount]
        label_list = [l.get_label() for l in lines_list]
        self.axes3_main.legend(lines_list, label_list, loc='upper left')

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

    def update_total_amount(self, x_uts_ms, y_total_ask, y_total_bid):
        '''update data'''
        # create x axis data
        x_data = x_uts_ms

        # update graph data
        self.buff_total_ask_amount = self.__update_buffer(
            self.buff_total_ask_amount,
            int(x_data),
            float(y_total_ask)
        )

        self.buff_total_bid_amount = self.__update_buffer(
            self.buff_total_bid_amount,
            int(x_data),
            float(y_total_bid)
        )

    def draw(self, x_offset):
        '''draw graph'''
        self.__draw_fig_1_1(x_offset)
        self.__draw_fig_2_1(x_offset)
        self.__draw_fig_3_1(x_offset)

    def __set_buff_lines(self, lines, axis_buff, x_offset):
        '''set buffer to lines'''
        buff_x = abs(axis_buff[:, 0] - x_offset)
        buff_y = axis_buff[:, 1]
        lines.set_xdata(buff_x)
        lines.set_ydata(buff_y)

    def __draw_fig_1_1(self, x_offset):

        x_lim_min = self.PRM_MAIN_PLOT_RANGE
        x_lim_max = self.PRM_MAIN_PLOT_OFFSET

        buff_y = self.buff_tick_price[:, 1]
        if len(buff_y) <= 0:
            buff_y = [0]
        y_lim_min = min(buff_y) - 50
        y_lim_max = max(buff_y) + 50

        self.__set_buff_lines(self.lines.tick_price, self.buff_tick_price, x_offset)
        self.axes1_main.set_xlim(x_lim_min, x_lim_max)
        self.axes1_main.set_ylim(y_lim_min, y_lim_max)

        self.__set_buff_lines(self.lines.tick_ask, self.buff_tick_ask, x_offset)
        self.axes_tick_ask.set_ylim(y_lim_min, y_lim_max)
        self.axes_tick_ask.set_yticks([], False)

        self.__set_buff_lines(self.lines.tick_bid, self.buff_tick_bid, x_offset)
        self.axes_tick_bid.set_ylim(y_lim_min, y_lim_max)
        self.axes_tick_bid.set_yticks([], False)

    def __draw_fig_2_1(self, x_offset):

        buff_y = self.buff_spread_price[:, 1]
        y_lim_min = min(buff_y) - 5
        y_lim_max = max(buff_y) + 10

        self.__set_buff_lines(self.lines.spread_price, self.buff_spread_price, x_offset)
        self.axes2_main.set_ylim(y_lim_min, y_lim_max)

    def __draw_fig_3_1(self, x_offset):

        buff_y_total_ask_amount = self.buff_total_ask_amount[:, 1]
        buff_y_total_bid_amount = self.buff_total_bid_amount[:, 1]

        wk_min_ask = min(buff_y_total_ask_amount)
        wk_min_bid = min(buff_y_total_bid_amount)
        y_lim_min = wk_min_ask if wk_min_ask < wk_min_bid else wk_min_bid
        y_lim_min = int(y_lim_min * 0.9)
        wk_max_ask = max(buff_y_total_ask_amount)
        wk_max_bid = max(buff_y_total_bid_amount)
        y_lim_max = wk_max_ask if wk_max_ask > wk_max_bid else wk_max_bid
        y_lim_max = int(y_lim_max * 1.1)

        self.__set_buff_lines(self.lines.total_bid_amount, self.buff_total_bid_amount, x_offset)
        self.axes3_main.set_ylim(y_lim_min, y_lim_max)

        self.__set_buff_lines(self.lines.total_ask_amount, self.buff_total_ask_amount, x_offset)
        self.axes_total_ask_amount.set_ylim(y_lim_min, y_lim_max)
        # self.axes_tick_ask.set_yticks([], False)


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

                self.graph.update_total_amount(
                    uts_ms_now,
                    ds.dsc_tick_fx.total_ask_amount,
                    ds.dsc_tick_fx.total_bid_amount
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
