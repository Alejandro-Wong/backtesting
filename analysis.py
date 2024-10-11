import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""
Various functions for analyzing and visualizing backtesting results after using bt.py to backtest
a strategy.

Work in Progress
"""

def returns_vs_drawdowns(backtest: object, mt_stats: pd.DataFrame, msc: str=''):
    return_v_dd = mt_stats[['Return [%]', 'Max. Drawdown [%]']].sort_values(by='Max. Drawdown [%]', ascending=False)
    fig, ax = plt.subplots(figsize=(12,10))
    ax.set_title(f'{backtest.strat_name}{msc} Return % vs Max Drawdown %')
    ax.bar(return_v_dd.index, return_v_dd['Return [%]'])
    ax.bar(return_v_dd.index, return_v_dd['Max. Drawdown [%]'])

    return fig


def ratios (backtest: object, mt_stats: pd.DataFrame, msc: str=''):
    df = mt_stats[['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']]

    x = np.arange(len(df.index))
    width = 0.25
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for ratio, num in df.items():
        offset = width * multiplier
        ax.bar(x + offset, num, width, label=ratio)
        multiplier += 1

    ax.set_ylabel('Ratio')
    ax.set_title(f'{backtest.strat_name}{msc} Ratios')
    ax.set_xticks(x + width, df.index)
    ax.tick_params(axis='x', labelrotation=45)
    ax.legend()

    return fig


def plot_equity_curves(backtest: object, mt_equity_curves:pd.DataFrame, msc: str=''):

    # Transform DataFrame to only show Equity
    unstack = mt_equity_curves.unstack().T
    df = unstack.loc['Equity']

    if df.index.name == 'Datetime':
        df = df.reset_index()
        df['Dates'] = pd.to_datetime(df['Datetime']).dt.date
        df = df.drop(columns=['Datetime'])
        df = df.set_index('Dates')

    # List symbols to iterate through
    symbols = list(df.columns)

    # Plot
    fig, ax = plt.subplots(figsize=(12,10))
    ax.set_title(f'{backtest.strat_name}{msc} Equity Curves')

    for symbol in symbols:
        equity = df[symbol]
        equity.plot()

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    return fig





