import pandas as pd
import os

'''
Miscellaneous functions and objects used in backtesting process
'''


def create_folders(path: str='', names: list[str]=None, for_backtesting: bool=True):
    """Create necessary folders for project"""
    if for_backtesting:
        names = ['ohlc','htmls','stats','trades','pdfs']
    else: names = names

    for name in names:
        try:
            os.mkdir(f'{path}{name}')
            print(f"Folder '{name}' created successfully.")
        except FileExistsError:
            print(f"Folder '{name}' already exists.")
        except OSError as e:
            print(f"Error creating folder '{name}' : {e}")



# OHLCV aggregation for resampling
ohlc_agg = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}


def resample_df(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample OHLCV data to desired frequency"""
    resample = df.resample(timeframe).apply(ohlc_agg).dropna()
    return resample



 
