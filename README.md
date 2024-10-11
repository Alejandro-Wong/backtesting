# Research and Backtesting of Technical Trading Strategies

This is a personal project that incorporates Zach Lûster's aka [kernc](https://github.com/kernc/backtesting.py) backtesting.py 
to backtest technical trading strategies. The objective is to create an organized system to backtest strategy ideas and analyze 
the results as efficiently as possible.


## Description of Modules

### ohlc.py
Contains two classes, GetOHLC and PrepOHLC.

- **GetOHLC** fetches historical Open, High, Low, Close (OHLC) data using either yfinance or alpaca APIs.<br>
It returns a cleaned dataframe with datetime as the index and converts the index to pandas datetime format in order<br>
to be compatible with kernc's backtesting.py library.

- **PrepOHLC** further prepares OHLC dataframe for backtesting by adding specific calculations and technical indicators<br>
directly to the dataframe as new columns.<br>

Note: most indicators can be calculated when constructing the strategy class later in the backtesting process. But for reasons currently 
beyond my understanding, certain indicators are not compatible with backtesting.backtesting.lib's barssince() method and cause an error 
when calculating the number of bars since a certain condition occured. These indicators are therefore added to PrepOHLC so that they can be compatible with such methods.

### config.py
Contains API key, secret key, and endpoint for alpaca api. Used by ohlc.py


### bt.py
Contains class BacktestingPy.<br>
Use kernc's backtesting.py to backtest either one ticker or multiple tickers simultaneously using <code>quick\_backtest()</code> and <code>multi\_ticker\_backtest()</code> method's respectively
Exports backtest visualizations in the form of htmls, as well as statistics summaries and trade logs in the form of csvs. These exported files are later used for
analysis and further strategy development.


### analysis.py
Contains various functions for analyzing and visualizing backtesting results after using bt.py to backtest a strategy.<br>
(This is the latest 'work in progress')


### utils.py
Contains miscellaneous functions that are used by ohlc.py and other .py files later in the backtesting process.



## The System (So Far)
So far, my backtesting system consists of a few steps. First and foremost being generating an idea.<br>
Once a strategy idea has been deemed worthy of testing, a folder is created for it. This folder will contain all the necessary subfolders and files involved in backtesting
the strategy idea. 

The next steps are as follows:

### Data Prep
A **data\_prep.py** file is created. This file creates the necessary subfolders that will be needed for backtesting
Along with this, this file downloads and preps all necessary OHLC data using ohlc.py. It then exports the data to csv and imports the cleaned csv's to be used in the next steps.
Sometimes, a separate file needs to be created for the strategy specific calculations that need to be added to the OHLC dataframes.

### Coding the Strategy
A **strategy.py** file is created. This is where a strategy is converted from idea to code using backtesting.py's Strategy class.<br>
Preliminary tests are done here to make sure the strategy is working as intended.

### Backtesting and Analysis
A **backtest.py** file is created. This is where the strategy can be tested and analyzed over multiple tickers or time periods. Parameter optimization can also be done here. Visualizations 
of certain statistics are exported as pdfs for further analyzation.

