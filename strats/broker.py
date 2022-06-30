import queue
from abc import abstractclassmethod
from datetime import datetime
from threading import Thread

import pandas as pd
from ibapi.client import Contract, EClient
from ibapi.order import Order
from ibapi.utils import iswrapper
from ibapi.wrapper import EWrapper

from feed import Feed


class Broker():

    def __init__(self,host,port,clientId,fund=0.0):
        # EWrapper.__init__(self)
        # EClient.__init__(self,wrapper=self)
        #self.connect(host,port,clientId)
        self.feed=Feed()
        self.feed.connect(host,port,clientId)
        self.fund=fund
        thread=Thread(target=self.run)
        thread.start()

    def init_error(self):
        error_queue=queue.Queue()
        self._errors=error_queue

    def is_error(self):
        return not self._errors.empty()
    
    def get_error(self,timeout=5):
        if self.is_error():
            try:
                return self._errors.get(timeout)
            except queue.Empty:
                return None
        return None

    def error(self,id,errorCode,errorString):
        error_message=("Interactive Brokers Error ID (%d), Error Code (%d) with response '%s"%(id,errorCode,errorString))
        self._errors.put(error_message)
    
    def init_time(self):
        time_queue=queue.Queue()
        self._time_queue=time_queue
        return time_queue
    
    def save_currentTime(self,server_time):
        self._time_queue.put(server_time)

    

    

    
