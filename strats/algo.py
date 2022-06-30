from broker import Broker
from instrument import Instrument
from ibapi.client import Contract

class Algo(Broker):
    
    def __init__(self, host='127.0.0.1', port=7497,clientId=0,fund=0.0):
        super().__init__(host, port, clientId,fund)
        # self.orderId=0
        self.price=[]
        # self.position=0.0

    
    def on_start(self,tickerId,contract,sleepTime:float,instrument:Instrument):
        self.reqCurrentTime()
        self.sleep()
        self.reqMktData(tickerId,contract=contract)

    def on_exit(self):
        self.disconnect()

    def on_tick(self,instrument:Instrument):
        pass

    def on_order(self):
        pass
    
    def on_fill():
        pass 

    def on_bar(bar_count:int,instrument:Instrument):
        pass

    def on_placeOrder(orderId,contract):
        pass

    def createContract(self,symbol,secType,exchange,currency):
        self.con=Contract()
        self.con.symbol=symbol
        self.con.secType=secType
        self.con.exchange=exchange
        self.con.currency=currency


    def request_history(self,symbol,start,end):
        return self.reqHis

if __name__=='__main__':
    algo=Algo()
    algo.run()