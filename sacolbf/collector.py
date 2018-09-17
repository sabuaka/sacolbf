# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: main class
'''
import threading
from enum import IntEnum, auto

from .manager import RTAPIManager
from .manager import MsgEvent
from .dataset import SADataset


class UpdateEvent(IntEnum):
    '''Change event type'''
    DEPTH = auto()
    TICK = auto()
    TRADE = auto()
    ERROR = auto()


class SACollector():
    '''Collector class'''

    __API_STOP_TIMEOUT = 30     # sec

    def __init__(self, event_callback=None, *, debug_mode=False):

        self.__event_callback = event_callback

        self._rtapi_mgr = RTAPIManager(msg_callback=self.__on_msg_event,
                                       err_callback=self.__on_err_event,
                                       elog=debug_mode)

        self.__thread_task_listening = None

        self.dataset = SADataset()

    def __on_msg_event(self, mgr, event, pair, data):  # fixed I/F pylint: disable-msg=W0613
        up_evt = UpdateEvent.ERROR

        if event == MsgEvent.BOARD_SS:
            self.dataset.analyze_depth_ss(pair, data)
            up_evt = UpdateEvent.DEPTH
        elif event == MsgEvent.BOARD_DF:
            self.dataset.analyze_depth_df(pair, data)
            up_evt = UpdateEvent.DEPTH

        if self.__event_callback:
            self.__event_callback(up_evt, self.dataset)

    def __on_err_event(self, mgr, ex):  # fixed I/F pylint: disable-msg=W0613
        if self.__event_callback:
            self.__event_callback(UpdateEvent.ERROR, None)

    def __task_proc_listning(self):
        self._rtapi_mgr.start()

    def start(self):
        '''Listen start'''
        self.__thread_task_listening = threading.Thread(target=self.__task_proc_listning)
        self.__thread_task_listening.start()

    def stop(self):
        '''Listen stop'''
        self._rtapi_mgr.stop()
        self.__thread_task_listening.join(timeout=self.__API_STOP_TIMEOUT)
