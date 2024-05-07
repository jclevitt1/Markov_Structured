"""
For now, structuring this as a single file instead of multiple feature selection abstractions.

Should be able to perform all feature selections with 3 HL functions, & a bunch of helpers. These functions would be:

1. Add PCT change.
2. Add STD.
3. Add technical analysis var's.

Eventually, want to be able to take in a list of supported features, and only add those features. To do this,
we simply need to keep a running list of all features selected, validate against this list, and have a map to each
function used to add that feature. Then just loop through these and call all the functions. We can do this much later,
but would be a doep exp
"""
import string
import ta
from ta.trend import MACD
import pandas as pd

def add_pct_change(data, col_in_q, col_to_add=None):
    if not col_to_add:
        col_to_add = f'{col_in_q}.PCT_CHANGE'
    data[col_to_add] = data[col_in_q].pct_change()

    def add_in_l_day_sd(self, data):
        name = 'STD_L=' + str(self.l)
        data[name] = data[self.col_to_std].rolling(window=self.l).std()
        return data, name

# L is the moving day period.
def add_std_change(data, col_in_q, col_to_add=None, L=20):
    if not col_to_add:
        col_to_add = 'STD_L=' + str(L)
    data[col_to_add] = data[col_in_q].rolling(window=L).std()

def add_basic_technical_analysis_vars(data, col_to_ma='daily_return', k=20, sd_multiplier=1.7):
    add_std_change(data, 'daily_return', L=k)
    add_sma_k_day_period(data, col_to_ma, k)
    add_ema_k_day_period(data, col_to_ma, k)
    add_rsi_k_day_period(data, col_to_ma, k)
    add_macd(data, col_to_ma, k // 3, k, k // 4)
    add_stochastic_oscillator(data, 'High', 'Low', 'Close', k // 3, k)
    add_bollinger_bands(data, col_to_ma='Close', window=k, num_std_dev=sd_multiplier)
    add_cmf(data, k)
    add_cci(data, k)
    add_volume_oscillator(data)
    add_force_index(data)
    add_on_balance_volume(data)
    add_aroon_oscillator(data)
    add_volume_price_trend(data)
    add_ultimate_oscillator(data)
    return data
    # Call a bunch of helper functions here

def add_sma_k_day_period(data, col_to_ma: string, k: int):
    sma_name = f'SMA_{k}'
    data[sma_name] = ta.trend.sma_indicator(data[col_to_ma], window=k)

def add_ema_k_day_period(data, col_to_ma: string, k: int):
    ema_name = f'EMA_{k}'
    data[ema_name] = ta.trend.ema_indicator(data[col_to_ma], window=k)

def add_macd(data, col_to_ma: str, short_period: int, long_period: int, signal_period: int):
    macd_name = 'MACD'
    macd_indicator = MACD(data[col_to_ma], window_fast=short_period, window_slow=long_period, window_sign=signal_period)
    data[macd_name] = macd_indicator.macd_diff()

def add_stochastic_oscillator(data, high_col: str, low_col: str, close_col: str, k_period: int, d_period: int):
    name = f'Stochastic_Oscillator_{k_period}_{d_period}'
    data[name] = ta.momentum.stoch(data[high_col], data[low_col], data[close_col], k_period, d_period)

def add_bollinger_bands(data, col_to_ma: str, window: int, num_std_dev: int):
    upper_band_name = 'Bollinger_Upper_Band'
    lower_band_name = 'Bollinger_Lower_Band'
    data[upper_band_name], data[lower_band_name] = ta.volatility.bollinger_hband(data[col_to_ma], window, num_std_dev), ta.volatility.bollinger_lband(data[col_to_ma], window, num_std_dev)

def add_rsi_k_day_period(data, col_to_ma: string, k: int):
    ema_name = f'RSI_{k}'
    data[ema_name] = ta.momentum.RSIIndicator(data[col_to_ma], window=k).rsi()

def add_cmf(data, k: int):
    cmf_name = f'CMF_{k}'
    data[cmf_name] = ta.volume.ChaikinMoneyFlowIndicator(data['High'], data['Low'], data['Close'], data['Volume'], window=k).chaikin_money_flow()

def add_cci(data, k: int, c: float = 0.015):
    cci_name = f'CCI_{k}'
    data[cci_name] = ta.trend.CCIIndicator(data['High'], data['Low'], data['Close'], window=k, constant=c).cci()

def add_volume_oscillator(data, short_window=12, long_window=26):
    short_ma = data['Volume'].rolling(window=short_window).mean()
    long_ma = data['Volume'].rolling(window=long_window).mean()
    data['volume_oscillator'] = short_ma - long_ma

def add_force_index(data, window=13):
    fi = (data['Close'] - data['Close'].shift(1)) * data['Volume']
    data['force_index'] = fi.rolling(window=window).mean()

def add_on_balance_volume(data):
    data['on_balance_volume'] = (data['Volume'] * (~data['Close'].diff().le(0) * 2 - 1)).cumsum()

def add_aroon_oscillator(data, window=25):
    aroon_indicator = ta.trend.AroonIndicator(data['High'], data['Low'], window=window)
    aroon_up = aroon_indicator.aroon_up()
    aroon_down = aroon_indicator.aroon_down()
    data['aroon_oscillator'] = aroon_up - aroon_down

def add_volume_price_trend(data):
    vpt = (data['Volume'] * ((data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1))).cumsum()
    data['volume_price_trend'] = vpt

def add_ultimate_oscillator(data, short_term=7, med_term=14, long_term=28):
    bp = data['Close'] - [min(low, close) for low, close in zip(data['Low'], data['Close'].shift(1))]
    tr = [max(high, close) - min(low, close) for high, low, close in zip(data['High'], data['Low'], data['Close'].shift(1))]
    avg7 = pd.Series(bp).rolling(window=short_term).sum() / pd.Series(tr).rolling(window=short_term).sum()
    avg14 = pd.Series(bp).rolling(window=med_term).sum() / pd.Series(tr).rolling(window=med_term).sum()
    avg28 = pd.Series(bp).rolling(window=long_term).sum() / pd.Series(tr).rolling(window=long_term).sum()
    data['ultimate_oscillator'] = (4 * avg7 + 2 * avg14 + avg28) / 7

def block_days(data, should_block_function):
    blocked = []
    for i in range(len(data)):
        if should_block_function(data.iloc[i]):
            pass
    return
