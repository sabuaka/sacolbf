# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: dataset parent class
'''
from sabitflyer.realtime import RealtimeAPI as RTAPI

from .dsc_depth import DatasetDepth
from .dsc_trade import DatasetTrade


class SADataset():
    '''Dataset parent class'''

    def __init__(self):
        self.dsc_depth_fx = DatasetDepth()
        self.dsc_trade_fx = DatasetTrade()

    def analyze_depth_ss(self, pair, data):
        '''analyze depth snapshot data'''
        if pair == RTAPI.TradePair.BTC_JPY.value:
            pass
        elif pair == RTAPI.TradePair.FX_BTC_JPY.value:
            self.dsc_depth_fx.init_data(data.mid_price, data.asks, data.bids, mpf=True)

    def analyze_depth_df(self, pair, data):
        '''analyze depth difference data'''
        if pair == RTAPI.TradePair.BTC_JPY.value:
            pass
        elif pair == RTAPI.TradePair.FX_BTC_JPY.value:
            self.dsc_depth_fx.update_data(data.mid_price, data.asks, data.bids, mpf=True)

    def analyze_trade(self, pair, data):
        '''analyze trade data'''
        if pair == RTAPI.TradePair.BTC_JPY.value:
            pass
        elif pair == RTAPI.TradePair.FX_BTC_JPY.value:
            self.dsc_trade_fx.update_date(data)
