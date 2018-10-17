# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: realtime api manager class
'''
from time import sleep
from enum import IntEnum, auto
import threading

from sabitflyer import RealtimeAPI
from sautility.dt import get_uts_s, get_dt_long


class MsgEvent(IntEnum):
    '''Enumeration events for callback notications'''
    BOARD_DF = auto()
    BOARD_SS = auto()
    TICKER = auto()
    EXECUTIONS = auto()


class RTAPIManager():
    '''RealtimeAPI manager'''
    # pylint: disable-msg=W0613

    __LISTEN_CHANNELS = [
        RealtimeAPI.ListenChannel.BOARD_SNAPSHOT_FX_BTC_JPY,
        RealtimeAPI.ListenChannel.BOARD_FX_BTC_JPY,
        RealtimeAPI.ListenChannel.EXECUTIONS_FX_BTC_JPY,
        RealtimeAPI.ListenChannel.TICKER_FX_BTC_JPY
    ]
    __API_PING_INTERVAL = 30    # sec
    __API_PING_TIMEOUT = 10     # sec
    __WD_TIMEOUT = 60           # sec

    def __out_elog(self, reason):
        if self.__elog:
            with open('error_RTAPIManager.log', 'a') as ef:
                ef.write(get_dt_long() + ': ' + reason + '\n')

    def __init__(self, msg_callback=None, *, err_callback=None, elog=False):

        self.__elog = elog

        self.__msg_callback = msg_callback
        self.__err_callback = err_callback

        self.__api_active = False
        self.__wd_time = None

        self.__rt_api = self.__create_rtapi()

        self.__thread_task_wd = None

    def __create_rtapi(self):
        '''create new realtime api instance.'''
        return RealtimeAPI(self.__LISTEN_CHANNELS,
                           on_message_board=self.__on_message_board,
                           on_message_board_snapshot=self.__on_message_board_snapshot,
                           on_message_ticker=self.__on_message_ticker,
                           on_message_executions=self.__on_message_executions,
                           on_error=self.__on_error,
                           ping_interval=self.__API_PING_INTERVAL,
                           ping_timeout=self.__API_PING_TIMEOUT)

    def __callback(self, event: MsgEvent, pair, data):
        '''callback to the registered method'''
        if self.__msg_callback:
            try:
                self.__msg_callback(self, event, pair, data)
            except:
                import traceback
                traceback.print_exc()

    def __on_message_board(self, rtapi, pair, board_data):
        self.__reset_wdt()
        self.__callback(MsgEvent.BOARD_DF, pair, board_data)

    def __on_message_board_snapshot(self, rtapi, pair, board_data):
        self.__reset_wdt()
        self.__callback(MsgEvent.BOARD_SS, pair, board_data)

    def __on_message_ticker(self, rtapi, pair, ticker_data):
        self.__reset_wdt()
        self.__callback(MsgEvent.TICKER, pair, ticker_data)

    def __on_message_executions(self, rtapi, pair, executions_data):
        self.__reset_wdt()
        self.__callback(MsgEvent.EXECUTIONS, pair, executions_data)

    def __on_error(self, rtapi, ex):
        self.__out_elog('reboot: websocket error')
        self.__rt_api = self.__create_rtapi()
        self.start()
        if self.__err_callback:
            self.__err_callback(self, ex)

    def __reset_wdt(self):
        self.__wd_time = get_uts_s()

    def __task_proc_watchdog(self):
        while self.__api_active:
            sleep(1)
            delta = get_uts_s() - self.__wd_time
            if delta > self.__WD_TIMEOUT:
                self.__out_elog('reboot: watchdog timeout')
                self.__rt_api = self.__create_rtapi()
                self.start()

    def start(self):
        '''Listen start'''
        # start watchdog
        self.__wd_time = get_uts_s()
        self.__thread_task_wd = threading.Thread(target=self.__task_proc_watchdog)
        self.__api_active = True
        self.__thread_task_wd.start()
        # start listening realtime api
        self.__rt_api.start()

    def stop(self):
        '''Listen stop'''
        # stop watchdog
        self.__api_active = False
        self.__thread_task_wd.join(3)
        # stop listening realtime api
        self.__rt_api.stop()
