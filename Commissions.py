class Commissions:
    amount= 0
    comms_type = ""
    COMMS_FIXED = 0
    COMMS_BPS = 1
    COMMS_PERCENTAGE = 2
    def __init__(self,amount, type):
        self.comms_type = type
        self.amount = amount
        return

    def calculate_commission(self, notional):
        if self.comms_type == self.COMMS_FIXED:
            return self.amount
        elif self.comms_type == self.COMMS_BPS:
            return self.amount*notional/10000
        elif self.comms_type == self.COMMS_PERCENTAGE:
            return self.amount * notional
        return 0

    
