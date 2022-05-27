from pandas import Series, DataFrame

IS_TALIB_ABSENT = False

try:
    import talib
except ImportError:
    IS_TALIB_ABSENT = True
    raise ImportError("TA-Lib is not installed.")

def _check_talib_availability():
    if IS_TALIB_ABSENT:
        raise ImportError("TA-Lib is not installed.")


def _extract_series(data):
    values = None

    if isinstance(data, Series):
        values = data.values
    else:
        if "last" in data.columns:
            values = data['last'].values
        elif "close" in data.columns:
            values = data['close'].values

    if values is None:
        raise ValueError(
            "Please note that data format must be pandas series or dataframe with at least a 'last' or 'close' column")

    return values


def _extract_ohlcv(data):
    if isinstance(data, DataFrame):
        if "open" in data.columns and "high" in data.columns \
                and "low" in data.columns and "close" in data.columns \
                and "volume" in data.columns:
            return data[['open', 'high', 'low', 'close', 'volume']].T.values

    raise ValueError("data must be pandas with OLHCV columns")


def BBANDS(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.BBANDS(prices, **kwargs)


def DEMA(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.DEMA(prices, **kwargs)


def EMA(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.EMA(prices, **kwargs)


def MA(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.MA(prices, **kwargs)


def MIDPRICE(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, _, _ = _extract_ohlcv(data)
    return talib.MIDPRICE(phigh, plow, **kwargs)


def SAR(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, _, _ = _extract_ohlcv(data)
    return talib.SAR(phigh, plow, **kwargs)

def SMA(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, _, _ = _extract_ohlcv(data)
    return talib.SMA(phigh, plow, **kwargs)

def WMA(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.WMA(prices, **kwargs)


def ADX(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.ADX(phigh, plow, pclose, **kwargs)


def MACD(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.MACD(prices, **kwargs)

def MFI(data, **kwargs):
    _check_talib_availability()
    popen, phigh, plow, pclose, pvolume = _extract_ohlcv(data)
    return talib.MFI(popen, phigh, plow, pclose, pvolume, **kwargs)


def ROC(data, **kwargs):
    _check_talib_availability()
    prices = _extract_series(data)
    return talib.ROC(prices, **kwargs)


def STOCH(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.STOCH(phigh, plow, pclose, **kwargs)

def AD(data, **kwargs):
    _check_talib_availability()
    popen, phigh, plow, pclose, pvolume = _extract_ohlcv(data)
    return talib.AD(popen, phigh, plow, pclose, pvolume, **kwargs)


def ADOSC(data, **kwargs):
    _check_talib_availability()
    popen, phigh, plow, pclose, pvolume = _extract_ohlcv(data)
    return talib.ADOSC(popen, phigh, plow, pclose, pvolume, **kwargs)



def AVGPRICE(data, **kwargs):
    _check_talib_availability()
    popen, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.AVGPRICE(popen, phigh, plow, pclose, **kwargs)

def WCLPRICE(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.WCLPRICE(phigh, plow, pclose, **kwargs)

def ATR(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.ATR(phigh, plow, pclose, **kwargs)


def NATR(data, **kwargs):
    _check_talib_availability()
    _, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.NATR(phigh, plow, pclose, **kwargs)


def CDLUNIQUE3RIVER(data, **kwargs):
    _check_talib_availability()
    popen, phigh, plow, pclose, _ = _extract_ohlcv(data)
    return talib.CDLUNIQUE3RIVER(popen, phigh, plow, pclose, **kwargs)