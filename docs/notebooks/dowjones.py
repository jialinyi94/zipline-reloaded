from zipline.typing import ZiplineContext, BarData
from zipline import run_algorithm
from zipline.api import symbol, order_target_percent
import pandas as pd
import matplotlib.pyplot as plt


def initialize(context: ZiplineContext) -> None:
    # which stock to trade
    dji = [
        'AAPL', 'AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'DIS', 'DOW', 'GS', 'HD',
        'IBM',
        'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PFE',
        'PG', 'TRV', 'UNH', 'VZ', 'WBA', 'WMT', 'XOM'
    ]
    context.dji_symbols = [symbol(s) for s in dji]
    context.index_average_window = 100


def handle_data(context: ZiplineContext, data: BarData) -> None:
    # get history for all the stocks
    stock_hist: pd.DataFrame = data.history(
        context.dji_symbols, "close", context.index_average_window, "1d"
    )

    # make an empty DataFrame to start with
    stock_analytics = pd.DataFrame()

    # add column for above or below average
    stock_analytics["above_mean"] = stock_hist.iloc[-1] > stock_hist.mean()

    # set weight for stocks to buy or sell
    num_stocks = stock_analytics["above_mean"].sum()
    if num_stocks > 0:
        stock_analytics.loc[stock_analytics["above_mean"], "weight"] = 1 / num_stocks
        stock_analytics.loc[~stock_analytics["above_mean"], "weight"] = 0.0
    else:
        stock_analytics["weight"] = 0.0

    # Iterate each row and place trades
    for stock, analytics in stock_analytics.iterrows():
        if data.can_trade(stock):
            order_target_percent(stock, analytics["weight"])


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
    start = pd.Timestamp('2001-01-01')
    end = pd.Timestamp('2025-01-01')

    run_algorithm(
        start=start,
        end=end,
        initialize=initialize,
        analyze=analyze,
        handle_data=handle_data,
        capital_base=10000,
        data_frequency='daily',
        bundle='us_equities',
    )
