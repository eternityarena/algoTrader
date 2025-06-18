from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
import threading
import time
import pandas as pd
from datetime import datetime
import ta.trend as ta_trend


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
        print("RealTimeBar. ReqId:", reqId, "Time:", str(datetime_t), "Open:", open_, "High:", high, "Low:", low, "Close:", close,
              "Volume:", volume)

        #print("Collecting data "+str(datetime_t))
        #detect start of 1 min bracket
        if datetime_t.second!=5 and datetime_t.second!=0:
            self.period_high = max(self.period_high,high)
            self.period_low = min(self.period_low,low)

        elif datetime_t.second==5:
            #start of OHLC
            self.period_flag = False
            self.period_open = open_
            self.period_high = high
            self.period_low = low
            self.period_close = close

        elif datetime_t.second==0:
            self.period_close = close
            self.period_high = max(self.period_high, high)
            self.period_low = min(self.period_low, low)
            if self.period_open!=0:
                temp = pd.DataFrame([[datetime_t,self.period_open,self.period_high,self.period_low,self.period_close,0]],
                                columns=['date','open','high','low','close','ema9']).set_index('date')
                self.prices = pd.concat([self.prices,temp], axis=0)
                self.period_flag = True



underlying = Contract()
underlying.symbol = "EUR"
underlying.secType = "CASH"
underlying.exchange = "IDEALPRO"
underlying.currency = "USD"

def ema_cal(close_t,ema_t0,day=9,smoothing=4):
    ema_data = (close_t*smoothing/(day+1)) + [ema_t0*(1 - smoothing/(day+1))]
def websocket_con():
    stitched = False
    print("Scanning for latest data")
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
                    app.reqHistoricalData(app.nextId(), underlying, time_str, str(num_sec-60)+" S", '1 Min', 'MIDPOINT', 1, 1, False, [])
                elif not stitched:
                    #stitch and calculate ema
                    print("Stitching")
                    stitched = True
                    app.prices = pd.concat([app.data,app.prices],axis  = 0)
                    ema9 = ta_trend.EMAIndicator(app.prices['close'], window=9, fillna=False)
                    app.prices['ema9'] = ema9.ema_indicator()

                    print(app.prices)
                    app.prices.to_csv("test.csv")
                else:
                    print("Why here?")

            last_price = app.prices.tail(1)
            if len(app.prices)>9:
                last_last_price = app.prices.tail(2).head(1)
                ema_t = ema_cal(last_price.close.iloc[0],last_last_price.ema9.iloc[0])
            elif len(app.prices==9):
                ema_t = ema_cal(last_price.close,app.prices.close.mean())
            elif len(app.prices<9):
                ema_t = 0

            app.period_flag = False
            print(app.prices)
            last_price['ema9'] = ema_t
            app.prices.update(last_price)

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


