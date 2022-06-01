import queue
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
from ibapi.order import Order 
import threading

class IBAPIClient(EClient):
    def __init__(self, wrapper):
        super().__init__(wrapper)
    
    def obtain_server_time(self):
        time_queue=self.wrapper.init_time()
        self.reqCurrentTime()
        try:
            server_time=time_queue.get(timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS)
        except queue.Empty:
            print("Time queue was empty or exceeded maximum timeout of ""%d seconds"%IBAPIClient.MAX_WAIT_TIME_SECONDS)
            server_time=None
        while self.wrapper.is_error():
            print(self.get_error())
        return server_time

class Broker(EWrapper,EClient):
    def __init__(self,ibAddr,ibPort,clientId):
        EWrapper.__init__(self)
        EClient.__init__(self,wrapper=self)
        thread=threading.Thread(target=self.run)
        thread.start()
        setattr(self,"_thread",thread)
        self.init_error()

        self.connect(ibAddr,ibPort,clientId)

    def run():
        pass