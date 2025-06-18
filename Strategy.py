import pandas as pd
from OrderManagement import OrderManagement
from Account import Account

class Strategy:
    name= ""
    prices = pd.DataFrame()
    account = None
    oms = None
    def __init__(self,name,prices,capital: float):
        self.name = name
        self.prices = prices.copy()
        self.account = Account(capital)
        self.oms = OrderManagement(self.account)
        return
    def next_t(self,price_t):
        return 0
    def buy_signals(self,price_t):
        return 0

    def sell_signals(self, price_t):
        return 0
    def send_orders_t(self,signal,price_t):
        return 0
    def backtest(self):
        for idx,price_t in self.prices.iterrows():
            print(idx)
            #process strategy
            self.next_t(price_t,idx)
            #process orders for order type such as trailing stop loss or stop or limit order.
            self.oms.process_orders(price_t)


        #calculate stats
        print(self.account.cash)
        #print("Outputing csv....")
        #self.account.holdings.to_csv("holdings_check.csv")
        #self.prices.to_csv("prices_check.csv")
        pd.merge(self.prices.reset_index(),self.account.holdings,left_on ='index',right_on='Time',how='left' ).to_csv("ledger.csv")