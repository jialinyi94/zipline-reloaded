# define typing hints
from zipline.typing import ZiplineContext, BarData
# import zipline functions
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol
# data manipulation
import pandas as pd
# import visualization
import matplotlib.pyplot as plt


def initialize(context: ZiplineContext):
    """
    Executed before the backtest starts.
    Set parameters and preparation.
    """
    # which stock to trade
    context.stock = symbol("IBM")
    # moving average window
    context.index_average_window = 100


def handle_data(context: ZiplineContext, data: BarData):
    """
    Request history for the stock
    """
    equity_hist: pd.Series = data.history(
        assets=context.stock,
        fields="close",
        bar_count=context.index_average_window,
        frequency='1d'
    )

    # if the current price is higher than the moving average
    if equity_hist.iloc[-1] > equity_hist.mean():
        stock_weight = 1.0
    else:
        stock_weight = 0.0

    # place order
    order_target_percent(asset=context.stock, target=stock_weight)


def analyze(context: ZiplineContext, perf: pd.DataFrame):
    fig = plt.figure(figsize=(12, 8))

    # First chart
    ax = fig.add_subplot(311)
    ax.set_title('Strategy Results')
    ax.semilogy(perf['portfolio_value'], linestyle='-', label='Equity Curve', linewidth=3.0)
    ax.legend()
    ax.grid(True)

    # Second chart
    ax = fig.add_subplot(312)
    ax.plot(perf['gross_leverage'], label='Exposure', linestyle='-', linewidth=1.0)
    ax.legend()
    ax.grid(True)

    # Third chart
    ax = fig.add_subplot(313)
    ax.plot(perf['returns'], label='Returns', linestyle='-.', linewidth=1.0)
    ax.legend()
    ax.grid(True)
    plt.savefig('results.png')


if __name__ == '__main__':
    start = pd.Timestamp('2001-01-03')
    end = pd.Timestamp('2025-03-20')

    run_algorithm(
        start=start,
        end=end,
        initialize=initialize,
        analyze=analyze,
        handle_data=handle_data,
        capital_base=10000,
        data_frequency='daily',
        bundle='us_equities'
    )
