import pandas as pd
from backtesting import Backtest


class BacktestingPy:
    """Backtest a strategy using backtesting.py on either one ticker or multiple tickers. Export
    backtest visualizations, stats and trades for further analyzation """

    def __init__(self, strategy: object, symbols: any=None, csv_path: str=None, html_path: str=None,
                 stats_path: str=None, trades_path: str=None, msc: str=''):
        
        self.strategy = strategy
        self.symbols = symbols
        self.csv_path = csv_path
        self.html_path = html_path
        self.stats_path = stats_path
        self.trades_path = trades_path
        self.msc = msc
        self.strat_name = self.strategy.__name__


    def clean_stats(self, stats: object) -> pd.Series:

        """
        Isolate and clean the stats section of the stats object that results
        from Backtest.run()
        """

        # Filter stats from stats object
        stats_index = []
        for i in range(28):
                stats_index.append(stats.index[i])
    
        stats_column = []
        for i in range(28):
                stats_column.append(stats[i])
    
        # Take filtered stats and create new pd.Series
        stats_new = pd.Series(stats_column, index=stats_index)

        # Round stats to two decimals
        two_decimal = pd.Series(
            [lambda x: 2 for x in range(19)], index=['Exposure Time[%]', 'Equity Final [$]',
                                                     'Equity Peak [$]', 'Return [%]', 'Buy & Hold Return [%]',
                                                     'Return (Ann.) [%]', 'Volatility (Ann.) [%]',
                                                     'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 
                                                     'Max. Drawdown [%]', 'Avg. Drawdown [%]', 'Win Rate [%]',
                                                     'Best Trade [%]', 'Worst Trade [%]', 'Avg. Trade [%]',
                                                     'Profit Factor', 'Expectancy [%]', 'SQN'])
        stats_new = stats_new.round(two_decimal)
    
        return stats_new
    

    def clean_trades(self, trades: pd.DataFrame) -> pd.DataFrame:

        """
        Isolate and clean the trades section of the stats object that results
        from Backtest.run()
        """

        # This method might eventually add columns to trades dataframe, for now it rounds to two decimal places
        
        two_decimal = pd.Series([2,2,2,2], index=(['EntryPrice','ExitPrice','PnL','ReturnPct']))
        trades = trades.round(two_decimal)

        return trades
    

    def multi_stats(self, stats_dict: dict) -> pd.DataFrame:

        """
        Convert dictionary containing multiple stats into pd.DataFrame
        """
        mt_stats_df = pd.DataFrame(stats_dict)
        mt_stats_df = mt_stats_df.T

        return mt_stats_df
    

    def multi_trades(self, trades_dict: dict) -> pd.DataFrame:

        """
        Converts dictionary containing multiple trades dataframes into
        a single pd.DataFrame
        """
        # mt_trades_df = pd.concat([trades_dict[df] for df in trades_dict])
        mt_trades_df = pd.concat(trades_dict)
    
        return mt_trades_df
    

    def multi_equity_curve(self, equity_curves_dict: dict) -> pd.DataFrame:

        """
        Converts dictionary of equity curves and drawdowns returned
        by multi_ticker_backtest() and converts it into a dataframe.
        """
        equity_df = pd.concat(equity_curves_dict)

        return equity_df
    

    def quick_backtest(self, df: pd.DataFrame, *, cash: int = 10000, commission: float = 0.0,
                             margin: float = 1.0, trade_on_close: bool = False,
                             hedging:bool = False, exclusive_orders: bool = False):
        
        bt = Backtest(df, self.strategy, cash=cash, commission=commission,
                    margin=margin, trade_on_close=trade_on_close, hedging=hedging,
                    exclusive_orders=exclusive_orders)
        
        stats = bt.run()
        trades = stats._trades

        # Export html, or plot when function runs
        if self.html_path:
            bt.plot(filename=f'{self.html_path}{self.symbols}_{self.strat_name}_{self.msc}.html', open_browser=False)
        else:
             bt.plot()
             
        # Export stats to csv
        if self.stats_path:
                stats.to_csv(f'{self.stats_path}{self.symbols}_{self.strat_name}_{self.msc}_stats.csv')
        # Export trades to csv        
        if self.trades_path:
                trades.to_csv(f'{self.trades_path}{self.symbols}_{self.strat_name}_{self.msc}_trades.csv')

        return stats
    


    def multi_ticker_backtest(self, cash: int = 10000, commission: float = 0.0,
                             margin: float = 1.0, trade_on_close: bool = False,
                             hedging:bool = False, exclusive_orders: bool = False
                             ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        """
        Performs a backtest on all stock tickers passed into 'symbols' parameter 
        using backtesting.py's Backtest class.

        Returns pd.DataFrame of all stats, trades, and equity curves for each backtest
        """

        # Empty Dictionaries
        stats_dict = {}
        trades_dict = {}
        equity_curves_dict = {}

        # Instantiate Backtests
        for symbol in self.symbols:
            if type(self.symbols) == dict:
                bt = Backtest(self.symbols[symbol], self.strategy, cash=cash, commission=commission,
                             margin=margin, trade_on_close=trade_on_close, hedging=hedging,
                             exclusive_orders=exclusive_orders)
                

            elif type(self.symbols) == list:
                df = pd.read_csv(f'{self.csv_path}{symbol}{self.msc}.csv', index_col=[0])
                df.index = pd.to_datetime(df.index)
                bt = Backtest(df, self.strategy, cash=cash, commission=commission,
                             margin=margin, trade_on_close=trade_on_close, hedging=hedging,
                             exclusive_orders=exclusive_orders)
            
        # Run Backtests. Store stats, trades, and equity curves in dictionaries
            full_stats = bt.run()

            stats = self.clean_stats(full_stats).fillna(0)
            trades = self.clean_trades(full_stats._trades)
            ec = full_stats._equity_curve

            stats_dict[symbol] = stats
            trades_dict[symbol] = trades
            equity_curves_dict[symbol] = ec[~ec.index.duplicated(keep='first')]

        # Export html plot, stats and trades to csvs
            if self.html_path:
                bt.plot(filename=f'{self.html_path}{symbol}_{self.strat_name}.html', open_browser=False)
        
            if self.stats_path:
                stats.to_csv(f'{self.stats_path}{symbol}_{self.strat_name}_stats.csv')
                
            if self.trades_path:
                trades.to_csv(f'{self.trades_path}{symbol}_{self.strat_name}_trades.csv')

        all_stats = self.multi_stats(stats_dict)
        all_trades = self.multi_trades(trades_dict)
        all_equity_curves = self.multi_equity_curve(equity_curves_dict)

                
        return all_stats, all_trades, all_equity_curves


    


        




   