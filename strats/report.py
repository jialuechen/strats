import argparse
import datetime
import hashlib
import logging
from time import time as timetime

import numpy as np
import pandas as pd
import psycopg2
from dateutil.parser import parse as parse_date
from flask import (Flask, jsonify, make_response, render_template, request,
                   send_from_directory)
from flask.json import JSONEncoder

import utils
from feed import Feed,load_feed_args
from strats import path


class Report():
    
    def __init__(self, feed=None, port=3000,host="0.0.0.0", password=None, **kwargs):
    
        self._password = password if password is not None else hashlib.sha1(
            str(datetime.datetime.now()).encode()).hexdigest()[:6]

        
        self.log = logging.getLogger(__name__)

      
        self.args = {arg: val for arg, val in locals().items(
        ) if arg not in ('__class__', 'self', 'kwargs')}
        self.args.update(kwargs)
        self.args.update(self.load_cli_args())

        self.dbconn = None
        self.dbcurr = None

        self.host = self.args['host'] if self.args['host'] is not None else host
        self.port = self.args['port'] if self.args['port'] is not None else port

        
        self.feed_name = self.args['feed'] if self.args['feed'] is not None else feed
        self.feed_args = load_feed_args(self.feed_name)
        self.feed = feed(**self.feed_args)


        self.dbconn = psycopg2.connect(
            host=str(self.feed_args['dbhost']),
            port=int(self.feed_args['dbport']),
            user=str(self.feed_args['dbuser']),
            passwd=str(self.feed_args['dbpass']),
            db=str(self.feed_args['dbname']),
            autocommit=True
        )
        self.dbcurr = self.dbconn.cursor()

    def load_cli_args(self):
        
        parser = argparse.ArgumentParser(description='Report',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('--port', default=self.args["port"],
                            help='HTTP port to use', type=int)
        parser.add_argument('--host', default=self.args["host"],
                            help='Host to bind the http process to')
        parser.add_argument('--feed',
                            help='Use this feed\'s MySQL server settings')
        parser.add_argument('--nopass',
                            help='Skip password for web app (flag)',
                            action='store_true')

        
        cmd_args, _ = parser.parse_known_args()
        args = {arg: val for arg, val in vars(
            cmd_args).items() if val != parser.get_default(arg)}
        return args

    def send_static(self, url_path):
        return send_from_directory('_webapp/', url_path)

    
    def login(self, password):
        if self._password == password:
            resp = make_response('yes')
            resp.set_cookie('password', password)
            return resp
        return make_response("no")

    
    def algos(self, json=True):
        algos = pd.read_sql("SELECT DISTINCT algo FROM trades",
                            self.dbconn).to_dict(orient="records")
        if json:
            return jsonify(algos)
        return algos

    def symbols(self, json=True):
        symbols = pd.read_sql("SELECT * FROM symbols",
                              self.dbconn).to_dict(orient="records")
        if json:
            return jsonify(symbols)
        return symbols

    def trades(self, start=None, end=None, algo_id=None, json=True):

        if algo_id is not None:
            algo_id = algo_id.replace('/', '')
        if start is not None:
            start = start.replace('/', '')
        if end is not None:
            end = end.replace('/', '')

        if start is None:
            start = utils.backdate("7D", date=None, as_datetime=False)

        trades_query = "SELECT * FROM trades WHERE exit_time IS NOT NULL"
        trades_where = []

        if isinstance(start, str):
            trades_where.append("entry_time>='" + start + "'")
        if isinstance(end, str):
            trades_where.append("exit_time<='" + end + "'")
        if algo_id is not None:
            trades_where.append("algo='" + algo_id + "'")

        if not trades_where:
            trades_query += " AND " + " AND ".join(trades_where)

        trades = pd.read_sql(trades_query, self.dbconn)
        trades['exit_time'].fillna(0, inplace=True)

        trades['slippage'] = abs(
            trades['entry_price'] - trades['market_price'])

        trades['slippage'] = np.where(
            ((trades['direction'] == "LONG") & (trades['entry_price'] > trades['market_price'])) |
            ((trades['direction'] == "SHORT") &
             (trades['entry_price'] < trades['market_price'])),
            -trades['slippage'], trades['slippage'])

        trades = trades.sort_values(
            ['exit_time', 'entry_time'], ascending=[False, False])

        trades = trades.to_dict(orient="records")
        if json:
            return jsonify(trades)
        return trades


    def positions(self, algo_id=None, json=True):

        if algo_id is not None:
            algo_id = algo_id.replace('/', '')

        trades_query = "SELECT * FROM trades WHERE exit_time IS NULL"
        if algo_id is not None:
            trades_query += " AND algo='" + algo_id + "'"

        trades = pd.read_sql(trades_query, self.dbconn)

        last_query = """SELECT s.id, s.symbol, max(t.last) as last_price
                        FROM ticks t LEFT JOIN symbols s ON (s.id=t.symbol_id)
                        GROUP BY s.id """
        last_prices = pd.read_sql(last_query, self.dbconn)

        trades = trades.merge(last_prices, on=['symbol'])

        trades['unrealized_pnl'] = np.where(
            trades['direction'] == "SHORT",
            trades['entry_price'] - trades['last_price'],
            trades['last_price'] - trades['entry_price'])

        trades['slippage'] = abs(
            trades['entry_price'] - trades['market_price'])
        trades['slippage'] = np.where(
            ((trades['direction'] == "LONG") & (trades['entry_price'] > trades['market_price'])) |
            ((trades['direction'] == "SHORT") &
             (trades['entry_price'] < trades['market_price'])),
            -trades['slippage'], trades['slippage'])

        trades = trades.sort_values(['entry_time'], ascending=[False])

        trades = trades.to_dict(orient="records")
        if json:
            return jsonify(trades)
        return trades

    def trades_by_algo(self, algo_id=None, start=None, end=None):
        trades = self.trades(start, end, algo_id=algo_id, json=False)
        return jsonify(trades)

   
    def bars(self, resolution, symbol, start=None, end=None, json=True):

        if start is not None:
            start = start.replace('/', '')
        else:
            start = utils.backdate("7D", date=None, as_datetime=False)

        if end is not None:
            end = end.replace('/', '')
            

        bars = self.feed.history(
            symbols=symbol,
            start=start,
            end=end,
            resolution=resolution
        )

        bars['datetime'] = bars.index

        bars = bars.to_dict(orient="records")
        if json:
            return jsonify(bars)
        return bars

   
    def index(self, start=None, end=None):
        if 'nopass' not in self.args:
            if self._password != "" and self._password != request.cookies.get('password'):
                return render_template('login.html')

        return render_template('dashboard.html')

    
    def run(self):
        app.add_url_rule('/', 'index', view_func=self.index)
        app.add_url_rule('/<path:start>', 'index', view_func=self.index)
        app.add_url_rule('/<start>/<path:end>', 'index', view_func=self.index)

        app.add_url_rule('/algos', 'algos', view_func=self.algos)
        app.add_url_rule('/symbols', 'symbols', view_func=self.symbols)

        app.add_url_rule('/positions', 'positions', view_func=self.positions)
        app.add_url_rule('/positions/<path:algo_id>',
                         'positions', view_func=self.positions)

        app.add_url_rule('/algo/<path:algo_id>',
                         'trades_by_algo', view_func=self.trades_by_algo)
        app.add_url_rule('/algo/<algo_id>/<path:start>',
                         'trades_by_algo', view_func=self.trades_by_algo)
        app.add_url_rule('/algo/<algo_id>/<start>/<path:end>',
                         'trades_by_algo', view_func=self.trades_by_algo)

        app.add_url_rule('/bars/<resolution>/<symbol>',
                         'bars', view_func=self.bars)
        app.add_url_rule(
            '/bars/<resolution>/<symbol>/<path:start>', 'bars', view_func=self.bars)
        app.add_url_rule('/bars/<resolution>/<symbol>/<start>/<path:end>',
                         'bars', view_func=self.bars)

        app.add_url_rule('/trades', 'trades', view_func=self.trades)
        app.add_url_rule('/trades/<path:start>',
                         'trades', view_func=self.trades)
        app.add_url_rule('/trades/<start>/<path:end>',
                         'trades', view_func=self.trades)
        app.add_url_rule('/login/<password>', 'login', view_func=self.login)
        app.add_url_rule('/static/<url_path>', 'send_static',
                         view_func=self.send_static)

        if 'nopass' not in self.args and self._password != "":
            print(" * Web app password is:", self._password)

        
        app.run(
            debug=True,
            host=str(self.host),
            port=int(self.port)
        )

class datetimeJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) | \
                isinstance(obj, datetime.date) | \
                isinstance(obj, datetime.time):
            return int(timetime())
        return JSONEncoder.default(self, obj)


app = Flask(__name__, template_folder=path['library'] + "/_webapp")
app.json_encoder = datetimeJSONEncoder

