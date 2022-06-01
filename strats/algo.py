from abc import abstractclassmethod
from broker import Broker

class Algo(Broker):
    def __init__(self, ibAddr, ibPort, clientId):
        super().__init__(ibAddr, ibPort, clientId)

    @abstractclassmethod
    def on_start():
        pass 
    
    @abstractclassmethod
    def on_fill():
        pass 

    @abstractclassmethod
    def on_bar():
        pass

    def retrieve_history(symbol,start,end):
        return self.feed.retrieve_history