import math
import datetime
import numpy as np
from utils.params import *
import OrderSamples
import ContractSamples
import AvailableAlgoParams
from collections import deque
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import BarData
from ibapi.tag_value import TagValue


class IBapiTest(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextValidOrderId = 0
        self.reqIds(-1)
        self.bar_1min = dict()
        self.bar_1min_parttime = np.array([])
        self.vwap = None
        self.vwap_moving = None
        self.account_buying_power_usd = TOTAL_BUY_POWER

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        super().updateAccountValue(key, val, currency, accountName)
        # print(f"current key is {key}, buying power is now {self.account_buying_power_usd}")
        if key == BUYING_POWER_KEY and accountName == ACCOUNT:
        # if accountName == ACCOUNT:
            self.account_buying_power_usd = float(val) / CURRENCY_CVT[currency]
            print(f"buying power is now {self.account_buying_power_usd}")
            # print("UpdateAccountValue. Key:", key, "Value:", val,
            # "Currency:", currency, "AccountName:", accountName, f"buying power is now {self.account_buying_power_usd}")

    # override
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        print(f"Setting nextValidOrderId: {orderId}")
        self.nextValidOrderId = orderId

    def historicalData(self, reqId: int, bar: BarData):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        self.update_bar_1min(bar)
        self.vwap = self.calc_bar_vwap_day()
        self.vwap_moving = self.calc_bar_vwap_moving()
        print(f"vwap {self.vwap}, moving vwap {self.vwap_moving}")


    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)


    def historicalDataUpdate(self, reqId: int, bar: BarData):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)
        self.update_bar_1min(bar)
        self.vwap = self.calc_bar_vwap_day()
        self.vwap_moving = self.calc_bar_vwap_moving()
        print(f"vwap {self.vwap}, moving vwap {self.vwap_moving}")

    def update_bar_1min(self, bar: BarData):
        time = bar.date[-8:]
        # tp = (bar.high + bar.low + bar.close) / 3
        tp = bar.average
        vol = bar.volume
        if time not in self.bar_1min:
            self.bar_1min_parttime = np.append(self.bar_1min_parttime, time)
            self.bar_1min[time] = {'tp': tp, 'vol': vol}
        else:
            self.bar_1min[time]['tp'] = tp
            self.bar_1min[time]['vol'] = vol

    def calc_bar_vwap_day(self):
        vol_total = 0
        val_total = 0
        for time in self.bar_1min:
            vol_total += self.bar_1min[time]['vol']
            val_total += self.bar_1min[time]['vol'] * self.bar_1min[time]['tp']
        vwap = val_total / vol_total
        return vwap

    def calc_bar_vwap_moving(self):
        vol_total = 0
        val_total = 0
        start_time_idx = len(self.bar_1min_parttime) - MOVING_VWAP_WINDOW \
            if len(self.bar_1min_parttime) - MOVING_VWAP_WINDOW > -1 else 0
        start_time = self.bar_1min_parttime[start_time_idx]
        for time in self.bar_1min:
            if time >= start_time:
                vol_total += self.bar_1min[time]['vol']
                val_total += self.bar_1min[time]['vol'] * self.bar_1min[time]['tp']
        vwap = val_total / vol_total
        return vwap


    def algo_order(self, action:str, quantity:int):
        baseOrder = OrderSamples.MarketOrder(action, quantity)
        AvailableAlgoParams.FillAdaptiveParams(baseOrder, "Normal")
        self.placeOrder(self.nextOrderId(), ContractSamples.USStockAtSmart(), baseOrder)

