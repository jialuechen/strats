import datetime
import time
import os
import sys
from stat import S_IWRITE
from math import ceil

# from decimal import *
import decimal

import numpy as np
import pandas as pd

from dateutil import relativedelta
from dateutil.parser import parse as parse_date
from pytz import timezone


decimal.getcontext().prec = 5



def read_single_argv(param, default=None):
    args = " ".join(sys.argv).strip().split(param)
    if len(args) > 1:
        args = args[1].strip().split(" ")[0]
        return args if "-" not in args else None
    return default

# ---------------------------------------------



def is_number(string):
    string = str(string)
    if string.isnumeric():
        return True
    try:
        float(string)
        return True
    except ValueError:
        return False


# ---------------------------------------------

def to_decimal(number, points=None):
    """ convert datatypes into Decimals """
    if not is_number(number):
        return number

    number = float(decimal.Decimal(number * 1.))  # can't Decimal an int
    if is_number(points):
        return round(number, points)
    return number


def gen_symbol_group(sym):
    sym = sym.strip()

    if "_FUT" in sym:
        sym = sym.split("_FUT")
        return sym[0][:-5] + "_F"

    elif "_CASH" in sym:
        return "CASH"

    if "_FOP" in sym or "_OPT" in sym:
        return sym[:-12]

    return sym

def chmod(f):
    """ change mod to writeable """
    try:
        os.chmod(f, S_IWRITE)  # windows (cover all)
    except Exception as e:
        pass
    try:
        os.chmod(f, 0o777)  # *nix
    except Exception as e:
        pass


def datetime64_to_datetime(dt):
    dt64 = np.datetime64(dt)
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
    return datetime.datetime.utcfromtimestamp(ts)


def round_to_fraction(val, res, decimals=None):
    """ round to closest resolution """
    if val is None:
        return 0.0
    if decimals is None and "." in str(res):
        decimals = len(str(res).split('.')[1])

    return round(round(val / res) * res, decimals)



def backdate(res, date=None, as_datetime=False, fmt='%Y-%m-%d'):
    """ get past date based on currect date """
    if res is None:
        return None

    if date is None:
        date = datetime.datetime.now()
    else:
        try:
            date = parse_date(date)
        except Exception as e:
            pass

    new_date = date

    periods = int("".join([s for s in res if s.isdigit()]))

    if periods > 0:

        if "K" in res:
            new_date = date - datetime.timedelta(microseconds=periods)
        elif "S" in res:
            new_date = date - datetime.timedelta(seconds=periods)
        elif "T" in res:
            new_date = date - datetime.timedelta(minutes=periods)
        elif "H" in res or "V" in res:
            new_date = date - datetime.timedelta(hours=periods)
        elif "W" in res:
            new_date = date - datetime.timedelta(weeks=periods)
        else:  # days
            new_date = date - datetime.timedelta(days=periods)

        # not a week day:
        while new_date.weekday() > 4:  # Mon-Fri are 0-4
            new_date = backdate(res="1D", date=new_date, as_datetime=True)

    if as_datetime:
        return new_date

    return new_date.strftime(fmt)



