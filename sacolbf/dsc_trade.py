# -*- coding: utf-8 -*-
'''
    - collector module -
    broker: bitFlyer
    part: dataset child class for trade
'''
from datetime import datetime, timedelta
from decimal import Decimal
from enum import IntEnum

from sautility.num import n2d


class DatasetTrade():
    '''class for dataset of depth'''

    BROKER_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    class TRADE_ARRAY(IntEnum):
        '''array position '''
        TIME = 0
        AMOUNT = 1
        BUY_ID = 2
        SELL_ID = 3

    def __init__(self, max_keep_sec=300):

        self.MAX_KEEP_SEC = max_keep_sec
        self.buys = []
        self.sells = []
        self.last_price = None

        self.__range_start_dt = None

    def is_available(self):
        '''data available'''
        if self.last_price is not None:
            return True
        return False

    def __add_data(self, exec_data):

        exec_dt = datetime.strptime(exec_data.exec_date[0:22], self.BROKER_TIMESTAMP_FORMAT)
        exec_amount = n2d(exec_data.size)
        exec_buy_id = exec_data.buy_child_order_acceptance_id
        exec_sell_id = exec_data.sell_child_order_acceptance_id

        if exec_data.side == "BUY":
            self.buys.append([exec_dt, exec_amount, exec_buy_id, exec_sell_id])
        elif exec_data.side == "SELL":
            self.sells.append([exec_dt, exec_amount, exec_buy_id, exec_sell_id])

    def __remove_rangeout_data(self):

        range_dt = datetime.utcnow() - timedelta(seconds=self.MAX_KEEP_SEC)

        def _create_new_list(target_list):
            new_lst = [ed for ed in target_list if ed[self.TRADE_ARRAY.TIME] > range_dt]
            target_list.clear()
            target_list.extend(new_lst)
            del new_lst

        _create_new_list(self.buys)
        _create_new_list(self.sells)

    def get_amount(self, sec=60):
        '''get trade amount -> buy, sell'''

        def _query_data(target_list, prm_range):

            if len(target_list) > 0:
                sum_amount = n2d(0.0)
                query_list = [ed for ed in target_list if ed[self.TRADE_ARRAY.TIME] >= prm_range]
                for exec_data in query_list:
                    sum_amount += exec_data[self.TRADE_ARRAY.AMOUNT]
                return sum_amount

            return n2d(0.0)

        prm_range = datetime.utcnow() - timedelta(seconds=sec)

        amount_buy = _query_data(self.buys, prm_range)
        amount_sell = _query_data(self.sells, prm_range)

        return amount_buy, amount_sell

    def get_exec_amount_buy(self, oid) -> Decimal:
        '''check excution for buy order'''
        exec_amount = n2d(0.0)
        for exec_data in self.buys:  # taker
            if exec_data[self.TRADE_ARRAY.BUY_ID] == oid:
                exec_amount += exec_data[self.TRADE_ARRAY.AMOUNT]
        for exec_data in self.sells:  # maker
            if exec_data[self.TRADE_ARRAY.BUY_ID] == oid:
                exec_amount += exec_data[self.TRADE_ARRAY.AMOUNT]
        return exec_amount

    def get_exec_amount_sell(self, oid) -> Decimal:
        '''check excution for sell order'''
        # for exec_data in self.sells:
        exec_amount = n2d(0.0)
        for exec_data in self.buys:  # maker
            if exec_data[self.TRADE_ARRAY.SELL_ID] == oid:
                exec_amount += exec_data[self.TRADE_ARRAY.AMOUNT]
        for exec_data in self.sells:  # taker
            if exec_data[self.TRADE_ARRAY.SELL_ID] == oid:
                exec_amount += exec_data[self.TRADE_ARRAY.AMOUNT]
        return exec_amount

    def update_date(self, raw_executions_list):
        '''update data'''

        # check start time
        if self.__range_start_dt is None:
            self.__range_start_dt = datetime.now()

        # add new data
        for exec_data in raw_executions_list:
            self.__add_data(exec_data)

        # remove out of range data
        self.__remove_rangeout_data()

        # get the last tread price
        self.last_price = raw_executions_list[-1].price
