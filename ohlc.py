import re
import pandas as pd
import numpy as np
import pandas_ta as ta
from pandas import DataFrame
from datetime import date, timedelta

from alpaca.data.historical import StockHistoricalDataClient 
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from config import API_KEY, SECRET_KEY
from utils import ohlc_agg

import yfinance as yf



class GetOHLC:
    """
    Download OHLC data using either yfinance or alpaca APIs.
     
    Returns clean dataframe with datetime as index and converts index to pandas datetime object 
    to be compatible with backtesting.py's backtesting framework
    """

    def __init__(self, 
                 symbol: str,           # ticker symbol. Format: 'ABC' (All caps)
                 period: str = '5y',    # lookback period from the end date, end date defaults to most recent trading day. 
                 interval: str = '1d',  # bar size
                 start: str = None,     # start date. Format: (YYYY-MM-DD) 
                 end: str = None,       # end date. Format: (YYYY-MM-DD)
                ):

     
        self.symbol = symbol
        self.period = period
        self.interval = interval 
        self.start = start
        self.end = end
        self.two_decimals = pd.Series([2,2,2,2], index=['Open', 'High','Low','Close']) # rounds OHLC data to two decimal places

    
    def from_yfinance(self) -> pd.DataFrame:
        """
        Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo 

        1m data cannot extend past 7 days
        2m - 30m data, and 90m data cannot extend past 60 days
        1h data cannot extend past 730 days
        1d - 3mo data allows max available data
        """

        # Start and end date specified
        if self.start != None and self.end != None:
            download = yf.download(self.symbol, period=self.period, interval=self.interval,
                               start=self.start, end=self.end, auto_adjust=False, 
                               progress=False, prepost=False)
        
        # Start and end date is None
        else: 
            download = yf.download(self.symbol, period=self.period, interval=self.interval,
                                auto_adjust=False, progress=False, prepost=False)

        # Round OHLC data to two decimal places, drop unneeded column, convert index to pd.datetime format 
        df = download.round(self.two_decimals)
        df.drop(columns='Adj Close', inplace=True)
        df.index = pd.to_datetime(download.index)
            
        return df
    

    def from_alpaca(self) -> pd.DataFrame:
        """
        As of 2024, data from 2016 to present (8 years) is available for all intervals.
        """
        # API and Secret Key, initialize historical data client
        api_key = API_KEY
        secret_key = SECRET_KEY
        client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)
    
        # Daily OHLCV requested
        if self.interval == '1d':

            # Start and end dates specified
            if self.start != None and self.end != None:
                start_date = self.start
                end_date = self.end

            # Start and end date not specified, period is in year ('y')
            elif self.start == None and self.end == None and 'y' in self.period:
                num_years = re.split('(\\d+)', self.period)
                start_date = date.today() - timedelta(days=365*int(num_years[1]))
                end_date = date.today() - timedelta(days=1)
                
            # Start and end date not specified, period is in days ('d')
            elif self.start == None and self.end == None and 'd' in self.period:
                num_days = re.split('(\\d+)', self.period)
                start_date = date.today() - timedelta(days=int(num_days[1]))
                end_date = date.today() - timedelta(days=1)
            
            # Start and end date not specified, no period specified, default period is 5 years
            else: 
                start_date = date.today() - timedelta(days=1825)
                end_date = date.today() - timedelta(days=1)

            # Request daily bars
            request_params = StockBarsRequest(
            symbol_or_symbols = self.symbol,
            timeframe=TimeFrame.Day,
            adjustment="split",
            start=start_date,
            end=end_date
            )

            # Raw DataFrame
            stock = client.get_stock_bars(request_params)
            raw_data = stock.df

            # OHLC data rounded two decimal places, index renamed and set to pd.datetime format, unneeded columns dropped
            df = raw_data.reset_index(level=0, drop=True)
            df = df.round(self.two_decimals)
            df.rename(columns={'open':'Open','high':'High',
                                'low':'Low','close':'Close',
                                'volume':'Volume'}, inplace=True)
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
            df.index = pd.to_datetime(df.index)
            df.drop(columns=['trade_count','vwap'], inplace=True)
            df.index.names = ['Date']
            df['Volume'] = df['Volume'].astype(int)

            return df
        
        # Intraday OHLCV requested
        else:
            
            # Start and end datetimes specified
            if self.start != None and self.end != None:

                start_datetime = pd.to_datetime(self.start, utc=True)
                end_datetime = pd.to_datetime(self.end, utc=True)

            # Default 'max' to 5 years worth of data
            elif self.start == None and self.end == None and self.period == 'max':
                start_datetime = date.today() - timedelta(days=1825)
                end_datetime = date.today() - timedelta(days=1)
            
            # Request year-to-date's worth of data
            elif self.start == None and self.end == None and self.period == 'ytd':
                start_datetime = date.today() - timedelta(days=365)
                end_datetime = date.today() - timedelta(days=1)

            # Request user defined number of years worth of data
            elif self.start == None and self.end == None and 'y' in self.period:
                num_years = re.split('(\\d+)', self.period)
                start_datetime=date.today() - timedelta(days=365*int(num_years[1]))
                end_datetime = date.today() - timedelta(days=1)
            
            # Request user defined number of days worth of data
            elif self.start == None and self.end == None and self.period != None:
                num_days = re.split('(\\d+)', self.period)
                start_datetime = date.today() - timedelta(days=int(num_days[1]))
                end_datetime = date.today() - timedelta(days=1)

            # Request user defined number of days from specified end date          
            elif self.start == None and self.end != None and self.period != None:
                if 'y' in self.period:
                    num_years = re.split('(\\d+)', self.period)
                    end_datetime = pd.to_datetime(self.end)
                    start_datetime = end_datetime - timedelta(days=365*int(num_years[1]))
                else:
                    num_days = re.split('(\\d+)', self.period)
                    end_datetime = pd.to_datetime(self.end)
                    start_datetime = end_datetime - timedelta(days=int(num_days[1]))

            # If no start or end datetime given, default to 100 days worth of data
            else:
                start_datetime = date.today() - timedelta(days=100)
                end_datetime = date.today() - timedelta(days=1)
            """
            '1h' data needs to be imported as 30min data then resampled,
            otherwise data starts at 09:00am
            """
            if self.interval == '1h' or self.interval == '30m':
                amount = 30
                end = '15:30'

            # Intraday interval determines last printed time value i.e '5m' data ends at 15:55
            else: 
                res = re.split('(\\d+)', self.interval)
                amount = int(res[1])
                endtime = timedelta(hours=16, minutes=00)
                end = str(endtime - timedelta(minutes=amount))
   
            # Request intraday bars
            request_params = StockBarsRequest(
                symbol_or_symbols = self.symbol,
                timeframe=TimeFrame(amount=amount, unit=TimeFrameUnit.Minute),
                adjustment="split",
                start=start_datetime,
                end=end_datetime
            )
            # Raw DataFrame
            stock = client.get_stock_bars(request_params)
            raw_data = stock.df

            # Reset index, fix timezone, set index to pd.datetime format, rename index
            df = raw_data.reset_index(level=0, drop=True)
            df = df[~df.index.duplicated(keep='first')]         # in case of duplicate index
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M:%S')
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize('UTC').tz_convert('US/Eastern')
            df.index = df.index.tz_localize(None)
            df.index.names = ['Datetime']


            # Fix column names, drop unneeded columns
            df = df.drop(columns=['trade_count','vwap'])
            df = df.rename(columns={'open':'Open','high':'High',
                            'low':'Low','close':'Close',
                            'volume':'Volume'})

            # Convert Volume column to integer format
            df['Volume'] = df['Volume'].astype(int)

            # Round OHLC data to two decimals
            df = df.round(self.two_decimals)

            # Filter data to only show ohlcv during open market hours (9:30 - 4:00)
            df = df.between_time('09:30', end)
            # print(df.head())


            # Resample 30m to 1h
            if self.interval == '1h':
                df = df.resample('1h', offset='30Min').apply(ohlc_agg).dropna().between_time('09:30', '15:30')
                return df     
            else:
                return df
            
    """
    To do: method for reading in and cleaning/converting any OHLC csv file downloaded from other sources
    """
    # def from_csv(self):
    #     ...


    def from_clean_csv(self,
                      csv_path: str,                  # Path of csv being read in  
                      msc: str='',                    # Misc string after symbol if any               
                      ) -> pd.DataFrame:
        
        """Reads in previously cleaned OHLC csv file while keeping datetime as index, and converts
        index to pandas datetime object to be compatible with backtest.py's backtesting framework"""

        """
        Method assumes OHLC csv being read in is saved in the following format:
        [path][symbol][optional string].csv

        ex. /Users/user/csv_files/AAPLdaily.csv
        """
        
        df = pd.read_csv(f'{csv_path}{self.symbol}{msc}.csv', index_col=[0])
        df.index = pd.to_datetime(df.index)

        return df
    
            

class PrepOHLC(DataFrame):
    """
    Prepare OHLC data for backtesting by adding necessary calculations -- such as 
    technical indicators -- as new columns to the OHLC DataFrame.
    """

    def previous_daily(self, value: str) -> 'PrepOHLC':
        
        """Previous Day's Open, High, Low, or Close"""

        allowed_values = ['open', 'high', 'low', 'close']

        if value.lower() not in allowed_values:
            raise ValueError(
                f"Invalid value '{value}'. Must be one of: {', '.join(allowed_values)}")
        
        pdv_string = f'prev_day_{value.lower()}'

        d1 = self.resample('1d').apply(ohlc_agg).dropna()
        d1 = d1.rename(columns={value.title(): pdv_string})
        prev_day_value = d1[pdv_string].shift(1).dropna()

        self = pd.merge_asof(self, prev_day_value, left_index=True, right_index=True).dropna()

        return PrepOHLC(self)
    
    
    def current_daily(self, value: str) -> 'PrepOHLC':

        """Current Day's Open, High, or Low"""

        allowed_values = ['open', 'high', 'low']

        if value.lower() not in allowed_values:
            raise ValueError(
                f"Invalid value '{value}'. Must be one of: {', '.join(allowed_values)}")
        
        if value.lower() == 'open':
            d1 = self.resample('1d').apply(ohlc_agg).dropna()
            d1 = d1.rename(columns={'Open':'curr_day_open'})
            curr_day_open = d1['curr_day_open']
            self = pd.merge_asof(self, curr_day_open, left_index=True, right_index=True)
        else:
            cdv_string = f'curr_day_{value.lower()}'
            if value.lower() == 'high':
                self[cdv_string] = self['High'].cummax()
            elif value.lower() == 'low':
                self[cdv_string] = self['Low'].cummin()
        
        return PrepOHLC(self)
    


    def opening_range(self, timeframe: int, range: int) -> 'PrepOHLC':

        """Opening range"""

        allowed_ranges = [5, 15, 30, 60, 90]

        if range not in allowed_ranges:
            raise ValueError(
                f"Invalid range {range}. Must choose between {', '.join(allowed_ranges)}"
            )

        if range == 60 or range == 90:
            resampled_df = self.resample(f"{str(range)}min", offset='30T').apply(ohlc_agg)
        else:
            resampled_df = self.resample(f"{str(range)}min").apply(ohlc_agg)

        opening_range = resampled_df.between_time('09:30', '09:30').drop(columns=['Open','Close', 'Volume']).dropna()
        opening_range = opening_range.rename(columns={'High':'or_high', 'Low':'or_low'})

        self = pd.merge_asof(self, opening_range, left_index=True, right_index=True)

        # Calculate opening range in datetime context
        start_range = pd.to_datetime('09:30:00').time()
        start_datetime = pd.Timestamp(year=2000, month=1, day=1,
                                    hour=start_range.hour, minute=start_range.minute, 
                                    second=start_range.second)
        end_datetime = start_datetime + pd.Timedelta(minutes=range - timeframe)
        end_range = end_datetime.time()

        # Mask for printing null until opening range is established, prevent look-ahead bias
        mask = (self.index.time >= start_range) & (self.index.time <= end_range)
        self.loc[mask, 'or_high'] = np.nan
        self.loc[mask, 'or_low'] = np.nan

        return PrepOHLC(self)
    
    def macd(self, fast: int=12, slow: int=26, signal: int=9) -> 'PrepOHLC':
        
        """Moving Average Convergence Divergence"""

        macd = ta.macd(self.Close, fast=fast, slow=slow, signal=signal)
        macd = macd.rename(columns={f'MACD_{fast}_{slow}_{signal}': 'macd',
                                    f'MACDh_{fast}_{slow}_{signal}': 'hist',
                                    f'MACDs_{fast}_{slow}_{signal}': 'signal'})

        self = self.join(macd).dropna()

        return PrepOHLC(self)

    def pivots(self, highs: str, lows: str, length: int=5, shift: int=None):
        
        """Find price swing highs and lows"""

        if shift == None:
            shift = 0
        else:
            shift=shift
        
        # Highs and Lows from dataframe
        highs = highs
        lows = lows

        pivot_highs = []
        pivot_lows = []

        for i in range(length, len(highs) - length):
            if (
                highs.iloc[i] > max(highs.iloc[i - length : i])
                and highs.iloc[i] > max(highs.iloc[i + 1 : i + length + 1])
            ):
                pivot_highs.append(i)
            if (
                lows.iloc[i] < min(lows.iloc[i - length : i])
                and lows.iloc[i] < min(lows.iloc[i + 1 : i + length + 1])
            ):
                pivot_lows.append(i)
        
        self['pivot_highs'] = highs.iloc[pivot_highs]
        self['pivot_lows'] = lows.iloc[pivot_lows]

        self['pivot_highs'] = self['pivot_highs'].shift(shift)
        self['pivot_lows'] = self['pivot_lows'].shift(shift)

        self['pivot_highs'] = self['pivot_highs'].ffill()
        self['pivot_lows'] = self['pivot_lows'].ffill()

        return PrepOHLC(self)
    

    def remove_cols(self, cols: list[str]) -> 'PrepOHLC':
        
        """Remove columns from dataframe"""

        self = self.drop(columns=cols)

        return PrepOHLC(self)
    

    def emas(self, length_s: list[int], dropna: bool=True) -> 'PrepOHLC':

        """Exponential Moving Average: A weighted moving average that gives more weight
        to recent price data"""

        for length in length_s:
            self[f'ema{length}'] = round(ta.ema(self.Close, length), 2)

        if dropna == False:
            return self
        else:
            self = self.dropna()

        return PrepOHLC(self)
    
    def atr(self, length: int=14, dropna: bool=True, shift: int=0) -> 'PrepOHLC':

        """Average True Range: A measure of volatility"""

        self['atr'] =  round(ta.atr(self.High, self.Low, self.Close, length), 2).shift(shift)

        if dropna == False:
            return self
        else: 
            self = self.dropna()

        return PrepOHLC(self)
    
    
    







        

        

        
    
