from Strategy import Strategy
import pandas as pd
from Commissions import Commissions
from Orders import Orders
import random
import ta.trend as ta_trend
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
class MyStrategy(Strategy):
    strat_commissions = Commissions(amount=2,type=Commissions.COMMS_FIXED)
    ema14 = None
    turning_point = {}
    min_max_df = None
    state = None
    ema_state =0
    def __init__(self, name, prices, capital: float):
        super().__init__(name,prices,capital)
        self.ema9 = ta_trend.EMAIndicator(prices['close'], window= 9, fillna = False)
        self.ema14 = ta_trend.EMAIndicator(prices['close'], window=14, fillna=False)
        self.prices['ema9'] = self.ema9.ema_indicator()
        self.prices['ema14'] = self.ema14.ema_indicator()
        self.turning_point= self.find_turning_points(data = self.prices['ema9'].to_list(),window_size=5)

        self.prices['ema9_max'] = [0 if x not in self.turning_point.keys()  else self.turning_point[x] for x in self.prices.index]
        self.min_max_df = self.prices[self.prices['ema9_max']!=0]
    def plot_data(self):
        plt.plot(self.prices.index,self.prices.ema9, label='Time Series')
        turning_point_x =  self.turning_point.keys()
        turning_point_y = [self.prices[self.prices.index == x]['ema9'] for x in self.turning_point.keys()]

        #get entry level
        buy_x = self.account.holdings[self.account.holdings['Quantity']>0].Time.to_list()
        buy_y = self.account.holdings[self.account.holdings['Quantity'] > 0]['Transaction Price'].to_list()
        plt.scatter(turning_point_x, turning_point_y, color='red', label='Turning Points',marker='s')
        plt.scatter(buy_x,buy_y, color='green', label='Buy',marker='o')
        sell_x = self.account.holdings[self.account.holdings['Quantity']>0].Time.to_list()
        sell_y = self.account.holdings[self.account.holdings['Quantity'] > 0]['Transaction Price'].to_list()
        #plt.scatter(turning_point_x, turning_point_y, color='red', label='Turning Points')
        plt.scatter(sell_x,sell_y, color='red', label='Sell',marker="x")
        plt.legend()
        plt.show()
    def find_turning_points(self,data, window_size=3):
        """Finds turning points (local min/max) in a time series using a sliding window."""
        turning_points = {}
        turning_points_type = []
        for i in range(2*window_size, len(data)):
            try:
                window = data[i - 2*window_size: i]
                center = window[window_size]
                if center == np.max(window):
                    turning_points[i]=1
                elif center == np.min(window+window):
                    turning_points[i]=-1
            except Exception as e:
                print("Error")

        return turning_points
    '''
    def next_t(self,price_t,idx):
        rnd_test = random.random()
        n=3
        if self.state is None:
            if np.isnan(price_t['ema9']):
                return
            else:
                last_n_turning = self.min_max_df[self.min_max_df.index<=idx]

                last_n_peak = last_n_turning[last_n_turning['ema9_max'] == 1].tail(n)
                last_n_bottom = last_n_turning[last_n_turning['ema9_max'] == -1].tail(n)
                if len(last_n_peak)>n-1 and len(last_n_bottom)>n-1:
                    if self.is_down_trend_reversal(last_n_peak['ema9'].to_list()) and self.is_down_trend_reversal(last_n_bottom['ema9'].to_list()):
                        if price_t.date==last_n_bottom['date'].tail(1).iloc[0]:
                        #if datetime.strptime(price_t.date, '%m/%d/%Y %H:%M') - last_n_bottom['date'].tail(1).iloc[0]>5:
                            print("Down Trend reversing")
                            self.state = "long"
                            self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                          commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                            #stop loss at previous top
                    elif self.is_down_trend_reversal([-1*x for x in last_n_peak['ema9'].to_list()]) and self.is_down_trend_reversal([-1*x for x in last_n_bottom['ema9'].to_list()]):
                        if price_t.date==last_n_peak['date'].tail(1).iloc[0]:
                            print("Up Trend reversing")
                            self.state = "short"
                            self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                                     commissions= self.strat_commissions,type=Orders.MARKET_ORDER,time_indicator=idx)
                    else:
                        print("No Trend")
        else:
            if self.state == 'long':
                last_turning = self.min_max_df[self.min_max_df.index == idx]
                if len(last_turning)>0:
                    if last_turning['ema9_max'].iloc[0] == 1:
                        self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                      commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                        self.state = None
            elif self.state == 'short':
                last_turning = self.min_max_df[self.min_max_df.index == idx]
                if len(last_turning) > 0:
                    if last_turning['ema9_max'].iloc[0] == -1:
                        self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                      commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                        self.state = None
        #if >0.5:
        #    print(rnd_test)
        #
    '''
    def next_t(self, price_t, idx):
        rnd_test = random.random()
        n = 3

        if self.state is None:
            if np.isnan(price_t['ema9']) or np.isnan(price_t['ema14']):
                if price_t['ema9']>price_t['ema14']:
                    self.ema_state = 1
                elif price_t['ema9']<price_t['ema14']:
                    self.ema_state = -1
                return
            else:
                if price_t['ema9']>price_t['ema14']+0.000001 and self.ema_state==-1:
                    # if datetime.strptime(price_t.date, '%m/%d/%Y %H:%M') - last_n_bottom['date'].tail(1).iloc[0]>5:
                    print("Down Trend reversing")
                    self.state = "long"
                    self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                 commissions=self.strat_commissions, type=Orders.MARKET_ORDER, time_indicator=idx)
                    # stop loss at previous top
                elif price_t['ema9']<price_t['ema14']-0.000001 and self.ema_state==1:
                    print("Up Trend reversing")
                    self.state = "short"
                    self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                  commissions=self.strat_commissions, type=Orders.MARKET_ORDER, time_indicator=idx)
                else:
                    print("No Trend")

                if price_t['ema9']>price_t['ema14']:
                    self.ema_state = 1
                elif price_t['ema9']<price_t['ema14']:
                    self.ema_state = -1

        else:
            if self.state == 'long':
                last_turning = self.min_max_df[self.min_max_df.index == idx]
                if len(last_turning) > 0:
                    if last_turning['ema9_max'].iloc[0] == 1 and price_t['ema9'] < price_t['ema14']:
                        self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                      commissions=self.strat_commissions, type=Orders.MARKET_ORDER, time_indicator=idx)
                        self.state = None
            elif self.state == 'short':
                last_turning = self.min_max_df[self.min_max_df.index == idx]
                if len(last_turning) > 0:
                    if last_turning['ema9_max'].iloc[0] == -1 and price_t['ema9'] > price_t['ema14']:
                        self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                                     commissions=self.strat_commissions, type=Orders.MARKET_ORDER, time_indicator=idx)
                        self.state = None

            if price_t['ema9'] > price_t['ema14']:
                self.ema_state = 1
            elif price_t['ema9'] < price_t['ema14']:
                self.ema_state = -1

    def is_increasing(self,series):
        for num in range(0,len(series)-1):
            if series[num]>series[num+1]:
                return False

        return True

    def is_down_trend_reversal(self,series):
        if series[0] > series[1]:
            for num in range(1,len(series)-1):
                if series[num]>series[num+1]:
                    return False

            return True
        return False


#load prices
#data = pd.read_csv("C:\\Users\\jian_\\PycharmProjects\\nn\\EURUSD_2W_13Apr202.csv")
data = pd.read_csv("C:\\Users\\jian_\\Documents\\algoTrader\\EURUSD_8W_15May2025.csv")

test_strat = MyStrategy("Mystrategy", data,50000)

test_strat.backtest()
test_strat.plot_data()
