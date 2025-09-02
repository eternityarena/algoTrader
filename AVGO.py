from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
import threading
import time
import pandas as pd
from datetime import datetime
import ta.trend as ta_trend
import numpy as np
from ibapi.order import Order as tws_order

class TradingApp(EWrapper, EClient):
    period_open,period_high,period_low,period_close=0,0,0,0
    prices = pd.DataFrame()
    bar_end_event = None
    period_flag = False
    orderId = 0
    data= pd.DataFrame()
    def __init__(self):
        EClient.__init__(self,self)

    def error(self, reqId, errorCode, errorString):
        print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)
    def nextId(self):
        self.orderId += 1
        return self.orderId


    def nextValidId(self, orderId):
        print('Next ID')
        self.nextValidOrderId = orderId
        self.start()
    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Price:", price)

    def start(self):
        # Define the contract (example: AAPL stock)
        contract = Contract()
        contract.symbol = "EUR"
        contract.secType = "CASH"
        contract.exchange = "IDEALPRO"
        contract.currency = "USD"

        # Request real-time bars
        self.reqRealTimeBars(1, contract, 5, "MIDPOINT", True, [])  # reqId, contract, barSize (seconds), whatToShow, useRTH, ignoreSize

    def historicalData(self, reqId, bar):

        temp = pd.DataFrame([[bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume]],columns=['date','open','high','low','close','volume'])
        temp['date'] = [datetime.strptime(x[0:17], '%Y%m%d %H:%M:%S') for x in temp['date']]
        temp.set_index("date",inplace=True)
        self.data = pd.concat([self.data,temp])
        print(reqId, bar)

    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical Data Ended for {reqId}. Started at {start}, ending at {end}")
        self.cancelHistoricalData(reqId)

    def stop(self):
        self.cancelRealTimeBars(1)
        self.close()

    def realtimeBar(self, reqId: int, time: int, open_: float, high: float, low: float, close: float, volume: int,
                    wap: float, count: int):
        datetime_t = datetime.fromtimestamp(time)
        #print("RealTimeBar. ReqId:", reqId, "Time:", str(datetime_t), "Open:", open_, "High:", high, "Low:", low, "Close:", close,
        #      "Volume:", volume)

        #print("Collecting data "+str(datetime_t))
        #detect start of 1 min bracket
        if datetime_t.second!=55 and datetime_t.second!=0:
            self.period_high = max(self.period_high,high)
            self.period_low = min(self.period_low,low)

        elif datetime_t.second==0:
            #start of OHLC
            self.period_flag = False
            self.period_open = open_
            self.period_high = high
            self.period_low = low
            self.period_close = close

        elif datetime_t.second==55:
            self.period_close = close
            self.period_high = max(self.period_high, high)
            self.period_low = min(self.period_low, low)
            if self.period_open!=0:
                datetime_t = datetime_t.replace(second=0, microsecond=0)
                temp = pd.DataFrame([[datetime_t,self.period_open,self.period_high,self.period_low,self.period_close,0]],
                                columns=['date','open','high','low','close','ema9']).set_index('date')
                self.prices = pd.concat([self.prices,temp], axis=0)
                self.period_flag = True



underlying = Contract()
underlying.symbol = "AVGO"
underlying.secType = "STK"
underlying.exchange = "SMART"
underlying.currency = "USD"
ema_period = 9
turning_point_window = 5
state = None
def ema_cal(close_t,ema_t0,day=9,smoothing=2):
    ema_data = (close_t*smoothing/(day+1)) + [ema_t0*(1 - smoothing/(day+1))]
    return ema_data

def find_turning_points(data,index, window_size=3):
    """Finds turning points (local min/max) in a time series using a sliding window."""
    turning_points = {}
    turning_points_type = []
    for i in range(window_size, len(data) - window_size):
        try:
            window = data[i - window_size: i + window_size + 1]
            center = window[window_size]
            if center == np.max(window):
                turning_points[index[i]]=1
            elif center == np.min(window):
                turning_points[index[i]]=-1
        except Exception as e:
            print("Error")

    return turning_points

def find_turning_points_t(data, window_size=3):
    """Finds turning points (local min/max) in a time series using a sliding window."""

    center = data[window_size]
    if center == np.max(data):
        return 1
    elif center == np.min(data):
        return -1
    else:
        return 0

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

#this is where we can directly copy from the backtest
def next_t(price_t,idx,min_max_df):
    global state
    #calculates min-max, turning point

    n=3
    if state is None:
        if np.isnan(price_t['ema9']):
            return
        else:
            last_n_turning = min_max_df[min_max_df.index<=idx]

            last_n_peak = last_n_turning[last_n_turning['ema9_max'] == 1].tail(n)
            last_n_bottom = last_n_turning[last_n_turning['ema9_max'] == -1].tail(n)
            if len(last_n_peak)>n-1 and len(last_n_bottom)>n-1:
                if is_down_trend_reversal(last_n_peak['ema9'].to_list()) and is_down_trend_reversal(last_n_bottom['ema9'].to_list()):
                    if price_t.date==last_n_bottom['date'].tail(1).iloc[0]:
                        print("Down Trend reversing")
                        state = "long"
                        print("BUY!!!")
                        #self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                        #             commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                        #stop loss at previous top
                elif is_down_trend_reversal([-1*x for x in last_n_peak['ema9'].to_list()]) and is_down_trend_reversal([-1*x for x in last_n_bottom['ema9'].to_list()]):
                    if price_t.date==last_n_peak['date'].tail(1).iloc[0]:
                        print("Up Trend reversing")
                        state = "short"
                        #self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                        #                         commissions= self.strat_commissions,type=Orders.MARKET_ORDER,time_indicator=idx)
                        print("SELL!!")
                else:
                    print("No Trend")
    else:
        if state == 'long':
            last_turning = min_max_df[min_max_df.index == idx]
            if len(last_turning)>0:
                if last_turning['ema9_max'].iloc[0] == 1:
                    #self.oms.sell(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                    #              commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                    print("SELL!!!")
                    state = None
        elif state == 'short':
            last_turning = min_max_df[min_max_df.index == idx]
            if len(last_turning) > 0:
                if last_turning['ema9_max'].iloc[0] == -1:
                    #self.oms.buy(ticker="EURUSD", quantity=20000, transact_price=price_t['close'],
                    #             commissions=self.strat_commissions, type=Orders.MARKET_ORDER,time_indicator=idx)
                    print("BUY!!!")
                    state = None
    #if >0.5:
    #    print(rnd_test)
    #


#this is where the strategy goes
def websocket_con():
    stitched = False
    print("Scanning for latest data")
    turning_point = {}
    min_max_df = None
    while True:
        time.sleep(1)
        if app.period_flag:
            print("latest data obtained, "+str(len(app.prices)>0 and not stitched))


            #check if stitch is required
            if len(app.prices)>0 and not stitched:
                print("req more data or stitch")
                first_live_datetime = app.prices.head(1).index[0]
                last_historical_datetime = app.data.tail(1).index[0]
                num_sec= (first_live_datetime-last_historical_datetime).seconds
                time_str = first_live_datetime.strftime('%Y%m%d %H:%M:%S') + " Asia/Singapore"
                if num_sec>60:
                    app.reqHistoricalData(app.nextId(), underlying, time_str, str(num_sec-60)+" Min", '15 Min', 'MIDPOINT', 1, 1, False, [])
                elif not stitched:
                    #stitch and calculate ema
                    print("Stitching")
                    stitched = True
                    app.prices = pd.concat([app.data,app.prices],axis  = 0)

                    #setting up data as per strategy
                    ema9 = ta_trend.EMAIndicator(app.prices['close'], window=ema_period, fillna=False)
                    app.prices['ema9'] = ema9.ema_indicator()

                    turning_point = find_turning_points(data=app.prices['ema9'].to_list(),
                                                        index= app.prices.index.to_list(),
                                                        window_size=turning_point_window)
                    app.prices['ema9_max'] = [0 if x not in turning_point.keys() else turning_point[x] for x
                                               in app.prices.index]
                    min_max_df = app.prices[app.prices['ema9_max'] != 0]

                    print(app.prices)
                    app.prices.to_csv("test.csv")
                else:
                    print("Why here?")

            else:
                last_price = app.prices.tail(1)
                last_last_price = app.prices.tail(2).head(1)
                ema_t = ema_cal(last_price.close.iloc[0], last_last_price.ema9.iloc[0])
                print("calculating EMA: close = "+str(last_price.close.iloc[0])+" last ema = "+str(last_last_price.ema9.iloc[0]))

                #turning point checks
                last_price['ema9_max']= find_turning_points_t(app.prices.tail(2*turning_point_window+1)['close'].to_list(),
                                                              window_size=turning_point_window)
                last_price['ema9'] = ema_t
                app.prices.update(last_price)
                next_t(last_price,min_max_df)
                app.prices.to_csv("simulated.csv")
            app.period_flag = False

def streamData():
    print("Starting to stream data...")
    app.reqMarketDataType(1)
    #app.reqMktData(reqId, underlying, "", False, False, [])
    #app.reqRealTimeBars(reqId, underlying, 5, "MIDPOINT", True, [])

def historicalData():
    print("Starting to download Historical data...")
    app.reqMarketDataType(1)
    time_str  = datetime.now().replace(second=0, microsecond=0).strftime('%Y%m%d %H:%M:%S')+" Asia/Singapore"
    hist_data_temp = app.reqHistoricalData(app.nextId(), underlying, time_str,"1 D",'1 Min','MIDPOINT',1,1,False,[])
    print(hist_data_temp)


port = 7496
reqId = 1
app = TradingApp()
app.connect("127.0.0.1", 7496, reqId)



con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)
historical_data_thread = threading.Thread(target=historicalData)
historical_data_thread.start()
time.sleep(1)

#stream_thread = threading.Thread(target=streamData)
#stream_thread.start()
#time.sleep(1)
app.run()
while True:
    #print("conthread",con_thread.is_alive())
    #print("streamthread",stream_thread.is_alive())
    time.sleep(1)


