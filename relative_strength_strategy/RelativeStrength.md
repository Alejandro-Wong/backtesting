# Relative Strength


## Background
Relative Strength and Weakness is a popular concept amongst retail traders that suggests that because the majority of stocks follow the overall market, it is possible to capitalize on stocks that are outperforming or underperforming the market. Stocks that are strong or weak relative to the market indicate institutional buying and selling. By finding these stocks, a retail trader can follow the "trail of breadcrumbs" left behind by the big financial institutions that move the market. [source](https://oneoption.com/intro-series/our-trading-methodology/)

Two notable communities that base their trading strategies on this idea is OneOption, led by veteran trader Peter Stolcers and subreddit r/RealDayTrading, founded by username HariSeldon.

Sidenote: 
Not to be confused with Relative Strength Index (RSI) which is an indicator that measures momentum and has nothing to do with the concept explained above.

## Relative Strength Calculation
The calculation of relative strength was developed by aforemetioned HariSeldon and turned into thinkscript code by username WorkPiece. The calculation is as follows:

marketRollingMove = (current market closing price) - (market closing price from x periods ago)
stockRollingMove = (current stock closing price) - (stock closing price from x periods ago)

marketRollingATR = x period Average True Range of market<br>
stockRollingATR = x period Average True Range of stock<br>

powerIndex = marketRollingMove / marketRollingATR<br>
expectedMove = powerIndex * stockRollingATR<br>
diff = stockRollingMove - expectedMove<br>
relativeStrength = diff / stockRollingATR<br>


## Incorporating 'Relative Strength' into a Trading Strategy
This strategy combines the concept of Relative Strength, with a basic intraday trend following strategy using the 8, 21, and 50 period exponential moving averages (EMAs)

### Buy Entry Conditions:
- Daily Relative Strength (5 periods) is above 0.5
- 5 Minute Relative Strength (12 periods) is above 0.5
- 8 EMA is above 21 EMA, and 21 EMA is above 50 EMA
- Price closes above all EMAs on a 5-minute timeframe

### Sell Entry Conditions:
- Daily Relative Strength (5 periods) is below 0.5
- 5 Minute Relative Strength (12 periods) is below 0.5
- 8 EMA is below 21 EMA, and 21 EMA is below 50 EMA
- Price closes below all EMAs on a 5-minute timeframe

### Stop Loss: 
- 4 ATR units (5 minute timeframe) away from entry

### Take Profit:
- TP1: 2 Risk units*
- TP2: 4 Risk units

*Risk unit = entry - stop loss, aka dollar-per-share risk
