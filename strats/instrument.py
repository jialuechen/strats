import math

from ibapi.client import Contract
from pandas import concat as pd_concat


class Instrument(str):
    parent = None
    tick_window = None
    bar_window = None

    
    def _set_parent(self, parent):
        
        self.parent = parent

    
    def _set_windows(self, ticks, bars):

        self.tick_window = ticks
        self.bar_window = bars

    
    @staticmethod
    def _get_symbol_dataframe(df, symbol):
        try:
            # this produce a "IndexingError using Boolean Indexing" (on rare occasions)
            return df[(df['symbol'] == symbol) | (df['symbol_group'] == symbol)].copy()
        except Exception as e:
            df = pd_concat([df[df['symbol'] == symbol],
                            df[df['symbol_group'] == symbol]], sort=True)
            df.loc[:, '_idx_'] = df.index
            return df.drop_duplicates(subset=['_idx_'], keep='last').drop('_idx_', axis=1)

    
    def get_bars(self, lookback=None, as_dict=False):
        
        bars = self._get_symbol_dataframe(self.parent.bars, self)

        # add signal history to bars
        bars = self.parent._add_signal_history(df=bars, symbol=self)

        lookback = self.bar_window if lookback is None else lookback
        bars = bars[-lookback:]
        # if lookback is not None:
        #     bars = bars[-lookback:]

        if not bars.empty > 0 and bars['asset_class'].values[-1] not in ("OPT", "FOP"):
            bars.drop(bars.columns[
                bars.columns.str.startswith('opt_')].tolist(),
                inplace=True, axis=1)

        if as_dict:
            bars.loc[:, 'datetime'] = bars.index
            bars = bars.to_dict(orient='records')
            if lookback == 1:
                bars = None if not bars else bars[0]

        return bars

    
    def get_bar(self):
        
        return self.get_bars(lookback=1, as_dict=True)

    
    def get_ticks(self, lookback=None, as_dict=False):
        
        ticks = self._get_symbol_dataframe(self.parent.ticks, self)

        lookback = self.tick_window if lookback is None else lookback
        ticks = ticks[-lookback:]
        # if lookback is not None:
        #     ticks = ticks[-lookback:]

        if not ticks.empty and ticks['asset_class'].values[-1] not in ("OPT", "FOP"):
            ticks.drop(ticks.columns[
                ticks.columns.str.startswith('opt_')].tolist(),
                inplace=True, axis=1)

        if as_dict:
            ticks.loc[:, 'datetime'] = ticks.index
            ticks = ticks.to_dict(orient='records')
            if lookback == 1:
                ticks = None if not ticks else ticks[0]

        return ticks

    
    def get_tick(self):
        return self.get_ticks(lookback=1, as_dict=True)

    
    def get_price(self):
        
        tick = self.get_ticks(lookback=1, as_dict=True)
        return None if tick is None else tick['last']

    
    def get_quote(self):
        
        if self in self.parent.quotes.keys():
            return self.parent.quotes[self]
        return None

    
    def get_orderbook(self):
        
        if self in self.parent.books.keys():
            return self.parent.books[self]

        return {
            "bid": [0], "bidsize": [0],
            "ask": [0], "asksize": [0]
        }

    
    def order(self, direction, quantity, **kwargs):
        
        self.parent.order(direction.upper(), self, quantity, **kwargs)

    
    def cancel_order(self, orderId):
        

        self.parent.cancel_order(orderId)

    
    def market_order(self, direction, quantity, **kwargs):
        
        kwargs['limit_price'] = 0
        kwargs['order_type'] = "MARKET"
        self.parent.order(direction.upper(), self, quantity=quantity, **kwargs)

    
    def limit_order(self, direction, quantity, price, **kwargs):
        
        kwargs['limit_price'] = price
        kwargs['order_type'] = "LIMIT"
        self.parent.order(direction.upper(), self, quantity=quantity, **kwargs)

    
    def buy(self, quantity, **kwargs):
        
        self.parent.order("BUY", self, quantity=quantity, **kwargs)

    
    def buy_market(self, quantity, **kwargs):
        
        kwargs['limit_price'] = 0
        kwargs['order_type'] = "MARKET"
        self.parent.order("BUY", self, quantity=quantity, **kwargs)

    
    def buy_limit(self, quantity, price, **kwargs):
        
        kwargs['limit_price'] = price
        kwargs['order_type'] = "LIMIT"
        self.parent.order("BUY", self, quantity=quantity, **kwargs)

    
    def sell(self, quantity, **kwargs):
        
        self.parent.order("SELL", self, quantity=quantity, **kwargs)

    
    def sell_market(self, quantity, **kwargs):
        
        kwargs['limit_price'] = 0
        kwargs['order_type'] = "MARKET"
        self.parent.order("SELL", self, quantity=quantity, **kwargs)

    
    def sell_limit(self, quantity, price, **kwargs):
        
        kwargs['limit_price'] = price
        kwargs['order_type'] = "LIMIT"
        self.parent.order("SELL", self, quantity=quantity, **kwargs)

    
    def exit(self):
        
        self.parent.order("EXIT", self)

    
    def flatten(self):
        
        self.parent.order("FLATTEN", self)

    
    def get_contract(self):
        
        return self.parent.get_contract(self)

    
    def get_contract_details(self):
        
        return self.parent.get_contract_details(self)

    
    def get_tickerId(self):
        
        return self.parent.get_tickerId(self)

    
    def get_combo(self):
        
        return self.parent.get_combo(self)

    
    def get_positions(self, attr=None):
        
        pos = self.parent.get_positions(self)
        try:
            if attr is not None:
                attr = attr.replace("quantity", "position")
            return pos[attr]
        except Exception as e:
            return pos

    
    def get_portfolio(self):
        
        return self.parent.get_portfolio(self)

    
    def get_orders(self):
        
        return self.parent.get_orders(self)

    
    def get_pending_orders(self):
        
        return self.parent.get_pending_orders(self)

    
    def get_active_order(self, order_type="STOP"):
        
        return self.parent.active_order(self, order_type=order_type)

    
    def get_trades(self):
        
        return self.parent.get_trades(self)

    
    def get_symbol(self):
        
        return self

    
    def modify_order(self, orderId, quantity=None, limit_price=None):
        
        return self.parent.modify_order(self, orderId, quantity, limit_price)

    
    def modify_order_group(self, orderId, entry=None, target=None, stop=None, quantity=None):
        
        return self.parent.modify_order_group(self, orderId=orderId,
                                              entry=entry, target=target,
                                              stop=stop, quantity=quantity)

    
    def move_stoploss(self, stoploss):
        
        stopOrder = self.get_active_order(order_type="STOP")

        if stopOrder is not None and "orderId" in stopOrder.keys():
            self.modify_order(orderId=stopOrder['orderId'],
                              quantity=stopOrder['quantity'], limit_price=stoploss)

    
    def get_margin_requirement(self):
        
        contract = self.get_contract()

        if contract.m_secType == "FUT":
            return futures.get_ib_futures(contract.m_symbol, contract.m_exchange)

        # else...
        return {
            "exchange": None,
            "symbol": None,
            "description": None,
            "class": None,
            "intraday_initial": None,
            "intraday_maintenance": None,
            "overnight_initial": None,
            "overnight_maintenance": None,
            "currency": None,
        }

    
    def get_max_contracts_allowed(self, overnight=True):
    
        timeframe = 'overnight_initial' if overnight else 'intraday_initial'
        req_margin = self.get_margin_requirement()
        if req_margin[timeframe] is not None:
            if 'AvailableFunds' in self.parent.account:
                return int(math.floor(self.parent.account['AvailableFunds'
                                                          ] / req_margin[timeframe]))

        return None

    def get_margin_max_contracts(self, overnight=True):
        
        return self.get_max_contracts_allowed(overnight=overnight)

    
    def get_ticksize(self):
        
        ticksize = self.parent.get_contract_details(self)['m_minTick']
        return float(ticksize)

    
    def pnl_in_range(self, min_pnl, max_pnl):
        
        portfolio = self.get_portfolio()
        return -abs(min_pnl) < portfolio['totalPNL'] < abs(max_pnl)

    
    def log_signal(self, signal):
        
        return self.parent._log_signal(self, signal)
