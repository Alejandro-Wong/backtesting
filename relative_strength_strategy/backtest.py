import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from aaw.bt import BacktestingPy
from aaw import analysis

from data_prep import dfs
from strategy import RelativeStrength


# Export Paths
htmls_path = './htmls/'
trades_path = './trades/'
stats_path = './stats/'
pdfs_path = './pdfs/'

# Backtest Object Initializations
strat_mt = BacktestingPy(RelativeStrength, dfs, html_path=htmls_path, stats_path=stats_path,
                            trades_path=trades_path)

# Multi-Ticker Backtest
mt_stats, mt_trades, mt_equity_curves = strat_mt.multi_ticker_backtest()

# Analysis
mt_return_v_dd = analysis.returns_vs_drawdowns(strat_mt, mt_stats)
mt_ec_plot = analysis.plot_equity_curves(strat_mt, mt_equity_curves)
mt_ratios = analysis.ratios(strat_mt, mt_stats)

# Export to pdf
with PdfPages(f'{pdfs_path}returns_vs_drawdowns.pdf') as pdf:
    pdf.savefig(mt_return_v_dd)

with PdfPages(f'{pdfs_path}equity_curves.pdf') as pdf:
    pdf.savefig(mt_ec_plot)

with PdfPages(f'{pdfs_path}ratios.pdf') as pdf:
    pdf.savefig(mt_ratios)


# plt.show()