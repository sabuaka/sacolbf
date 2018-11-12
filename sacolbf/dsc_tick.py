# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: dataset child class for tick
'''
from datetime import datetime, timedelta
from enum import IntEnum

from sabitflyer import RealtimeAPI as RTAPI
from sautility.num import n2d


class DatasetTick():
    '''class for dataset of tick'''

    BROKER_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    class TRADE_PRICE_ARRAY(IntEnum):
        '''array position '''
        TIME = 0
        PRICE = 1

    def __init__(self, keep_time):

        self.__prm_keep_time = keep_time
        self.__available = False

        self.ts_dt = None
        self.bid_price = None
        self.ask_price = None
        self.bid_amount = None
        self.ask_amount = None
        self.total_bid_amount = None
        self.total_ask_amount = None
        self.trade_price = None
        self.trade_volume_24h = None
        self.spread = None
        self.spread_rate = None
        self.price_list = []
        self.price_max = None
        self.price_min = None

    def is_available(self):
        '''data available'''
        return self.__available

    def prmset_keep_time(self, value):
        '''set parameter of keep_time'''
        self.__prm_keep_time = value

    def __update_price_list(self, dt, price):
        # add new data
        self.price_list.append([dt, price])

        # remove rangeout data
        range_dt = datetime.now() - timedelta(seconds=self.__prm_keep_time)
        new_lst = [ed for ed in self.price_list if ed[self.TRADE_PRICE_ARRAY.TIME] > range_dt]
        self.price_list.clear()
        self.price_list.extend(new_lst)
        del new_lst

        # calculate maximum and minimum
        prices = [row[1] for row in self.price_list]
        self.price_max = max(prices)
        self.price_min = min(prices)

    def update_date(self, data: RTAPI.TickerData):
        '''update data'''
        self.__available = False

        wk_utc_dt = datetime.strptime(data.timestamp[0:22], self.BROKER_TIMESTAMP_FORMAT)
        self.ts_dt = wk_utc_dt + timedelta(hours=9)
        self.bid_price = n2d(data.best_bid)
        self.ask_price = n2d(data.best_ask)
        self.bid_amount = n2d(data.best_bid_size)
        self.ask_amount = n2d(data.best_ask_size)
        self.total_bid_amount = n2d(data.total_bid_depth)
        self.total_ask_amount = n2d(data.total_ask_depth)
        self.trade_price = n2d(data.ltp)
        self.trade_volume_24h = n2d(data.volume_by_product)
        self.spread = self.ask_price - self.bid_price
        self.spread_rate = (self.ask_price / self.bid_price) - n2d(1.0)

        self.__update_price_list(self.ts_dt, self.trade_price)

        self.__available = True
