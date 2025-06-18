import pandas as pd
from Orders import Orders
from Commissions import Commissions
class Account:
    capital = 0
    cash = 0
    limits = 0
    transaction_history = pd.DataFrame()
    holdings = pd.DataFrame()
    cash_positions = pd.DataFrame()
    margin = 0
    def __init__(self, capital):
        self.capital = capital
        self.cash = capital
        self.limits = capital
        self.cash_positions = pd.DataFrame([[-1,capital,0,0]],['Time','Cash','Realized PnL','Unrealized PnL'])
    def check_transaction(self,order,amount):

        if self.cash > abs(amount):
            return True
        else:
            return False

    def transact(self,amount, order:Orders, transaction_price):

        transaction_df = pd.DataFrame([[order.time_indicator,order.order_ticker, order.order_quantity,
                                        order.get_commission(transaction_price), transaction_price,
                                        order.total_order_cost(transaction_price), 'open', 0, 0, 0, 0]],
                                      columns=['Time','Ticker', 'Quantity', 'Entry Commissions', 'Transaction Price',
                                               'Total Cost'
                                          , 'Status', 'Closing Price', 'Closing Commission', 'Realized', 'Unrealized'])

        self.holdings = pd.concat([self.holdings, transaction_df], axis=0)
        consolidated_df = self.holdings.groupby('Ticker').sum()
        realized_pnl = -consolidated_df[consolidated_df['Quantity']==0]['Total Cost'].sum()
        self.cash = self.capital+realized_pnl
        realized_pnl = -consolidated_df[consolidated_df['Quantity'] == 0]['Total Cost'].sum()


