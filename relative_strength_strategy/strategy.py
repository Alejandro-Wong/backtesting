import datetime
from backtesting import Strategy, Backtest
import pandas_ta as ta

class RelativeStrength(Strategy):
    def init(self):

        # RRS
        def rrs_d1(df):
            return df['rrs_d1']
        
        def rrs_m5(df):
            return df['rrs_m5']
        
        self.rrs_d1 = self.I(rrs_d1, self.data, color='red')
        self.rrs_m5 = self.I(rrs_m5, self.data, color='blue')

        # ATR
        self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 12, plot=False)
        
        # EMAs
        self.ema8 = self.I(ta.ema, self.data.Close.s, 8, color='teal')
        self.ema21 = self.I(ta.ema, self.data.Close.s, 21, color='red')
        self.ema50 = self.I(ta.ema, self.data.Close.s, 50, color='gray')

        # Time Constraints
        self.entry_min = datetime.time(9, 35)
        self.entry_max = datetime.time(15, 30)
        self.exit = datetime.time(15,45)

    def next(self):
        time = self.data.index[-1].time()
        price = self.data.Close[-1]

        ema8 = self.ema8
        ema21 = self.ema21
        ema50 = self.ema50

        rrs_d1 = self.rrs_d1
        rrs_m5 = self.rrs_m5 

        atr = self.atr


        # Stop loss calculation
        def stop(long: bool=True):
            if not long:
                sl = price + (4 * atr)
            else:
                sl = price - (4 * atr)
            return sl

        # Risk per share calculation
        def r(long: bool=True):
            if not long:
                r = stop() - price
            else:
                r = price - stop()
            return r
        
        # Buy / Sell logic
        if not self.position and self.entry_min <= time <= self.entry_max:
            if (
                rrs_d1 > 0.5
                and rrs_m5 > 0.5
                and price > ema8 > ema21 > ema50
            ):
                self.buy(size=50, sl=stop(), tp=price + (r() * 2))
                self.buy(size=50, sl=stop(), tp=price + (r() * 4))

            elif (
                rrs_d1 < -0.5
                and rrs_m5 < -0.5
                and price < ema8 < ema21 < ema50
            ):
                self.sell(size=50, sl=stop(long=False), tp=price - (r() * 2))
                self.sell(size=50, sl=stop(long=False), tp=price - (r() * 4))

        if self.position.is_long:
            if price < ema8 < ema21 < ema50 or time > self.exit:
                self.position.close()
        elif self.position.is_short:
            if price > ema8 > ema21 > ema50 or time > self.exit:
                self.position.close()


# Quick test before moving on to multi-ticker backtest

import data_prep as data
bt = Backtest(data.dfs['AAPL'], RelativeStrength, cash=6000, margin=0.03)
stats = bt.run()
bt.plot()

print(stats)