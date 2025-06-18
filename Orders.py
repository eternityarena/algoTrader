import Commissions
class Orders:
    account = None
    order_type = None
    order_price = None
    order_quantity = None
    order_commissions = None
    MARKET_ORDER = 0
    LIMIT_ORDER = 1
    order_ticker = None
    time_indicator = None

    def __init__(self,commissions:Commissions, account,type,price,quantity,ticker,time):
        self.order_commissions = commissions
        self.account = account
        self.order_type = type
        self.order_price = price
        self.order_quantity = quantity
        self.order_ticker = ticker
        self.time_indicator = time

    def get_order_type(self):
        return self.order_type

    def total_order_cost(self,price):
        return self.order_quantity*price+self.get_commission(price)

    def get_commission(self,price):
        return self.order_commissions.calculate_commission( self.order_quantity*price)


    def get_margin(self,price):
        #assume 100% margin
        return abs(self.order_quantity)*price+self.get_commission(price)