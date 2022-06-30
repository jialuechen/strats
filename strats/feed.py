from abc import abstractclassmethod
import queue
import sys
from threading import Thread

import psycopg2
import pandas as pd
from ibapi.client import Contract, EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

from strats import __version__, path

class Feed(EWrapper,EClient):
    def __init__(self,host,port,clientId,dbhost="localhost", dbport="3306", dbname="strats",dbuser="root", dbpass="", dbskip=False) -> None:
        EWrapper.__init__(self)
        EClient.__init__(self,wrapper=self)
        self.connect(host,port,clientId)

        thread=Thread(target=self.run)
        thread.start()

    def init_error(self):
        error_queue=queue.Queue()
        self._errors=error_queue
        self.reqHistoricalData

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

    def create_history(self,symbol:str,start,end=None,resolution='1T',is_continuous=True):
        if isinstance(symbols, str):
            symbols = symbols.split(',')

        #symbol_groups = list(symbols)

        try:
            start = start.strftime(["DATE_TIME_FORMAT_LONG_MILLISECS"])
        except Exception as e:
            pass

        if end is not None:
            try:
                end = end.strftime(["DATE_TIME_FORMAT_LONG_MILLISECS"])
            except Exception as e:
                pass

        # connect to pgsql
        self.pgsql_connect()

        # --- build query
        table = 'ticks' if resolution[-1] in ("K", "V", "S") else 'bars'

        query = """SELECT tbl.*,
            CONCAT(s.`symbol`, "_", s.`asset_class`) as symbol, s.symbol_group, s.asset_class, s.expiry,
            g.price AS opt_price, g.underlying AS opt_underlying, g.dividend AS opt_dividend,
            g.volume AS opt_volume, g.iv AS opt_iv, g.oi AS opt_oi,
            g.delta AS opt_delta, g.gamma AS opt_gamma,
            g.theta AS opt_theta, g.vega AS opt_vega
            FROM `{TABLE}` tbl LEFT JOIN `symbols` s ON tbl.symbol_id = s.id
            LEFT JOIN `greeks` g ON tbl.id = g.{TABLE_ID}
            WHERE (`datetime` >= "{START}"{END_SQL}) """.replace(
            '{START}', start).replace('{TABLE}', table).replace('{TABLE_ID}', table[:-1] + '_id')

        if end is not None:
            query = query.replace('{END_SQL}', ' AND `datetime` <= "{END}"')
            query = query.replace('{END}', end)
        else:
            query = query.replace('{END_SQL}', '')

        if symbols[0].strip() != "*":
            if is_continuous:
                query += """ AND ( s.`symbol_group` in ("{SYMBOL_GROUPS}") or
                CONCAT(s.`symbol`, "_", s.`asset_class`) IN ("{SYMBOLS}") ) """
                query = query.replace('{SYMBOLS}', '","'.join(symbols)).replace(
                    '{SYMBOL_GROUPS}', '","'.join(symbol_groups))
            else:
                query += """ AND ( CONCAT(s.`symbol`, "_", s.`asset_class`) IN ("{SYMBOLS}") ) """
                query = query.replace('{SYMBOLS}', '","'.join(symbols))
        # --- end build query

        # get data using pandas
        data = pd.read_sql(query, self.dbconn)  # .dropna()

        # no data in db
        if data.empty:
            return data

        # clearup records that are out of sequence
        data = self._fix_history_sequence(data, table)

        # setup dataframe
        return prepare_history(data=data, resolution=resolution, tz=tz, continuous=True)

    def retrieve_history(self, symbol,start,end):
        self.pgsql_connect()

    def pgsql_connect(self):
        if self.args['dbskip']:
            return 
        if self.dbcurr is not None or self.dbconn is not None:
            return
        self.dbconn=self.get_postgresql_connection()
        self.dbcurr=self.dbconn.cursor()

        self.dbcurr.execute("SHOW TABLES")
        tables=[table[0] for table in self.dbcurr.fetchall()]
        required=["bars","symbols","trades","greeks","_version_"]
        if all(item in tables for item in required):
            self.dbcurr.execture("SELECT version FROM `_version_`")
            db_version=self.dbcurr.fetchone()
            if db_version is not None and __version__==db_version[0]:
                return
        self.dbcurr.execute(open(path['library'] + '/schema.sql', "rb").read())
        try:
            self.dbconn.commit()
            sql = "TRUNCATE TABLE _version_; INSERT INTO _version_ (`version`) VALUES (%s)"
            self.dbcurr.execute(sql, (__version__))
            self.dbconn.commit()

            self.dbcurr.close()
            self.dbconn.close()

            self.dbconn = self.get_postgresql_connection()
            self.dbcurr = self.dbconn.cursor()

        except Exception as e:
            self.dbconn.rollback()
            self._remove_cached_args()
            sys.exit(1)

    def get_postgresql_connection(self):
        if self.args['dbskip']:
            return None

        return psycopg2.connect(
            host=str(self.args['dbhost']),
            port=int(self.args['dbport']),
            user=str(self.args['dbuser']),
            passwd=str(self.args['dbpass']),
            db=str(self.args['dbname'])
        )

    def register(self,instruments:dict):
        instruments = list(instruments.values())

        if not isinstance(instruments, list):
            return

        db = pd.read_csv(self.args['symbols'], header=0).fillna("")

        instruments = pd.DataFrame(instruments)
        instruments.columns = db.columns

        db = db.append(instruments)
        db = db.drop_duplicates(keep="first")

        db.to_csv(self.args['symbols'], header=True, index=False)

    @iswrapper
    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, distance: str, benchmark: str, projection: str, legsStr: str):
        super().scannerData(reqId, rank, contractDetails, distance, benchmark, projection, legsStr)
    
    @iswrapper
    def scannerDataEnd(self, reqId: int):
        super().scannerDataEnd(reqId)

    @iswrapper
    def scannerParameters(self, xml: str):
        super().scannerParameters(xml)
        dataframe=pd.read(xml)
        dataframe.to_csv("scanner.csv")
        open('scanner.txt','w',encoding='utf-8').write(xml)


    @iswrapper
    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)

    @iswrapper
    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)
    
    @iswrapper
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
    
    @iswrapper
    def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
        super().openOrder(orderId, contract, order, orderState)
    
    @iswrapper
    def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
    
    @iswrapper
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)

    @iswrapper
    def positionEnd(self):
        super().positionEnd()

    @iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)

    @iswrapper
    def tickByTickMidPoint(self, reqId: int, time: int, midPoint: float):
        super().tickByTickMidPoint(reqId, time, midPoint)

    @iswrapper
    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float, bidSize: int, askSize: int, tickAttribBidAsk: TickAttribBidAsk):
        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
    
    @iswrapper
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float, size: int, tickAttribLast: TickAttribLast, exchange: str, specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAttribLast, exchange, specialConditions)
    
    @iswrapper
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)

    @iswrapper
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)

    @iswrapper
    def tickGeneric(self, reqId: TickerId, tickType: TickType, value: float):
        super().tickGeneric(reqId, tickType, value)

    @iswrapper
    def realtimeBar(self, reqId: TickerId, time: int, open_: float, high: float, low: float, close: float, volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
    
    @iswrapper
    def historicalData(self, reqId: int, bar: BarData):
        super().historicalData(reqId, bar)

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)

    @iswrapper
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        super().historicalDataUpdate(reqId, bar)

    @iswrapper
    def historicalTicks(self, reqId: int, ticks: ListOfHistoricalTick, done: bool):
        super().historicalTicks(reqId, ticks, done)

    @iswrapper
    def historicalTicksBidAsk(self, reqId: int, ticks: ListOfHistoricalTickBidAsk, done: bool):
        super().historicalTicksBidAsk(reqId, ticks, done)

    @iswrapper
    def historicalTicksLast(self, reqId: int, ticks: ListOfHistoricalTickLast, done: bool):
        super().historicalTicksLast(reqId, ticks, done)
    
    @iswrapper
    def fundamentalData(self, reqId: TickerId, data: str):
        super().fundamentalData(reqId, data)

    @iswrapper
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)

    @abstractclassmethod
    def createContract(self,symbol,secType,exchange,currency):
        pass

    @iswrapper
    def currentTime(self, time: int):
        super().currentTime(time)

def load_feed_args():
    pass

if __name__=="__main__":
    feed=Feed()
    feed.run()
