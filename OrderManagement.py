from Orders import Orders
from Account import Account
from Commissions import Commissions
class OrderManagement:
    buy_order = None
    sell_order = None
    account = None
    holdings = None

    def __init__(self,account:Account):
        self.account = account
        return

    def buy(self, ticker, quantity, transact_price, commissions: Commissions,time_indicator,type=Orders.MARKET_ORDER):
        print("Buy Order = "+str(self.buy_order))
        if self.buy_order==None:
            self.buy_order = Orders(commissions = commissions,price = transact_price,type = type,quantity = quantity,
                                account=self.account,ticker = ticker,time=time_indicator)
        return

    def sell(self, ticker, quantity, transact_price, commissions: Commissions,time_indicator,type=Orders.MARKET_ORDER):
        if self.sell_order==None:
            self.sell_order = Orders(commissions = commissions,price = transact_price,type = type,quantity = -quantity,
                                account=self.account,ticker = ticker,time=time_indicator)
        return

    def process_orders(self,price_t):
        if self.buy_order is not None:
            if self.buy_order.get_order_type() == Orders.MARKET_ORDER:

                transacted_price = price_t['close']
                margin_cost = self.buy_order.get_margin(transacted_price)
                total_cost = self.buy_order.total_order_cost(transacted_price)
                can_transact = self.account.check_transaction(self.buy_order,margin_cost)
                if can_transact:
                    print("Buying")
                    self.account.transact(total_cost,self.buy_order,transacted_price)
                else:
                    print("Insufficient fund")
                self.buy_order = None
        if self.sell_order is not None:

            if self.sell_order.get_order_type() == Orders.MARKET_ORDER:
                transacted_price = price_t['close']
                margin_cost = self.sell_order.get_margin(transacted_price)
                total_cost = self.sell_order.total_order_cost(transacted_price)
                can_transact = self.account.check_transaction(self.sell_order,margin_cost)
                if can_transact:
                    print("Selling")
                    self.account.transact(total_cost,self.sell_order,transacted_price)
                    self.sell_order = None
                else:
                    print('Insufficient Fund, not selling')

            return