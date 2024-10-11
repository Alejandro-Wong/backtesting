import pandas as pd
from ohlc import GetOHLC

# Wilders Average for rrs_atr
def wilders_average(values, n):
    return values.ewm(alpha=1 / n, adjust=False).mean()

# ATR calculation for Real Relative Strength
def rrs_atr(df, n=14):
    data = df.copy()
    high = data['High']
    low = data['Low']
    close = data['Close']
    data['tr0'] = (high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].shift().max(axis=1)    
    atr = wilders_average(tr, n)

    return atr

# Real Relative Strength calculation
'''
Credit to HariSeldon2020 and WorkPiece from r/RealDayTrading for coming up with the calculation.
Calculates "Real Relative Strength" of an asset compared to the overall market
'''
def rrs(df: pd.DataFrame, mkt: pd.DataFrame, rrs_length: int, shift: int=0) -> pd.Series:

    mkt_r = mkt.Close - mkt.Close.shift(rrs_length)
    df_r = df.Close - df.Close.shift(rrs_length)

    mkt_atr = rrs_atr(mkt, n=rrs_length)
    df_atr = rrs_atr(df, n=rrs_length)

    power_index = mkt_r / mkt_atr
    expected_move = power_index * df_atr
    diff = df_r - expected_move
    real_relative_strength = round(diff / df_atr, 3)

    rrs = pd.Series(real_relative_strength, index=df.Close.index)

    return rrs



