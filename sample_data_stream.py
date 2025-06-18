from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):
        self.nextValidOrderId = orderId
        self.start()

    def historicalData(self, reqId:int, bar: BarData):
        print("HistoricalData. ReqId:", reqId, "BarData", bar)

    def historicalDataEnd(self, reqId: int, startDateStr: str, endDateStr: str):
        print("HistoricalDataEnd. ReqId:", reqId, "from", startDateStr, "to", endDateStr)

    def realtimeBar(self, reqId: int, time: int, open_: float, high: float, low: float, close: float, volume: int, wap: float, count: int):
        print("RealTimeBar. ReqId:", reqId, "Time:", time, "Open:", open_, "High:", high, "Low:", low, "Close:", close, "Volume:", volume)

    def tickPrice(self, reqId, tickType, price: float, attrib):
        print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Price:", price)

    def tickSize(self, reqId, tickType, size: int):
        print("TickSize. TickerId:", reqId, "tickType:", tickType, "Size:", size)

    def contractDetails(self, reqId: int, contractDetails):
        print("Contract Details:", contractDetails)


    def start(self):
        # Define the contract (example: AAPL stock)
        contract = Contract()
        contract.symbol = "EUR"
        contract.secType = "CASH"
        contract.exchange = "IDEALPRO"
        contract.currency = "USD"

        # Request real-time bars
        self.reqRealTimeBars(1, contract, 5, "MIDPOINT", True, [])  # reqId, contract, barSize (seconds), whatToShow, useRTH, ignoreSize


    def stop(self):
        self.cancelRealTimeBars(1)
        self.close()

app = TestApp()
app.connect("127.0.0.1", 7496, 2) # Replace with your IBKR connection details
app.run()