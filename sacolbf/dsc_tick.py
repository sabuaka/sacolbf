# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: dataset child class for tick
'''
from datetime import datetime, timedelta

from sabitflyer import RealtimeAPI as RTAPI
from sautility.num import n2d


class DatasetTick():
    '''class for dataset of tick'''

    BROKER_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    def __init__(self):
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

        self.__available = False

    def is_available(self):
        '''data available'''
        return self.__available

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

        self.__available = True
