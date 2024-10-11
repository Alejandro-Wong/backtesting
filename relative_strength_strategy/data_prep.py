import os
import pandas as pd
from utils import create_folders, resample_df
from ohlc import GetOHLC, PrepOHLC
from relative_strength import rrs

create_folders()

# Global Variables
ohlc_path = './ohlc/'
mkt = 'SPY'
symbols = ['AAPL','TSLA','MU','AMZN','XOM','AMD','QQQ','META', 'GOOGL','ORCL','JPM','V',
           'COST','MCD','SPOT','ADBE','CAT','HD','NFLX','MA']
period = '2y'
interval = '5m'
end = '2019-01-03'

# Download / Export Market (SPY) Data
if not os.path.exists(f"{ohlc_path}{mkt}_{period}_{interval}.csv"):

    mkt_dl = GetOHLC(mkt, period=period, interval=interval, end=end).from_alpaca()
    mkt_dl.to_csv(f'{ohlc_path}{mkt}_{period}_{interval}.csv')

print(f'{period} of {interval} data for {mkt} successfully loaded')


# Import / Resample Market (SPY) Data
spy = GetOHLC(mkt).from_clean_csv(ohlc_path, f'_{period}_{interval}')
spy_d1 = resample_df(spy, '1d')


# Download / Prep OHLC for list of symbols / Export to CSV
for symbol in symbols: 
    if not os.path.exists(f"{ohlc_path}{symbol}_{period}_{interval}.csv"):

        df = GetOHLC(symbol, period=period, interval=interval, end=end).from_alpaca()   
        df_d1 = resample_df(df, '1d')
        df_d1['rrs_d1'] = rrs(df_d1, spy_d1, 5, shift=1)

        rrs_df_d1 = df_d1[['rrs_d1']].dropna()

        df_prep = PrepOHLC(df).atr()
        df_prep['rrs_m5'] = rrs(df, spy, 12)
        df_merge = pd.merge_asof(df_prep, rrs_df_d1, left_index=True, right_index=True)
        df_merge.to_csv(f'{ohlc_path}{symbol}_{period}_{interval}.csv')               
    else:
        continue

print(f'{period} of {interval} data for symbols in symbol list are successfully loaded')


# Import Prepped OHLC for list of symbols to dictionary 
dfs = {}
for symbol in symbols:
    df = GetOHLC(symbol).from_clean_csv(ohlc_path, f'_{period}_{interval}')
    dfs[symbol] = df