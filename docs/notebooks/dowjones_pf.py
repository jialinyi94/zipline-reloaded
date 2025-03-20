from zipline import run_algorithm
from zipline.api import order_target_percent, symbol
from zipline.api import schedule_function, date_rules, time_rules

from zipline.typing import ZiplineContext

import pandas as pd
import pyfolio as pf


def initialize(context: ZiplineContext):
    # which stocks to trade
    dji = [
        "AAPL",
        "AXP",
        "BA",
        "CAT",
        "CSCO",
        "CVX",
        "DIS",
        "DWDP",
        "GS",
        "HD",
        "IBM",
        "INTC",
        "JNJ",
        "JPM",
        "KO",
        "MCD",
        "MMM",
        "MRK",
        "MSFT",
        "NKE",
        "PFE",
        "PG",
        "TRV",
        "UNH",
        "UTX",
        "V",
        "VZ",
        "WMT",
        "XOM",
    ]
    # make symbol list from tickers
    context.stocks = [symbol(s) for s in dji]

    # set trading params
    context.history_window = 20
    context.stocks_to_hold = 10

    # schedule the daily trading routine for once per month
    schedule_function(
        func=handle_data,
        date_rule=date_rules.month_start(),
        time_rule=time_rules.market_close()
    )


def month_perf(x):
    perf = (x[-1] / x[0]) - 1
    return perf


def handle_data(context: ZiplineContext, data: pd.DataFrame):
    # get historical data
    hist: pd.DataFrame = data.history(
        context.stocks, "close", context.history_window, "1d"
    )

    # this creates a table of percent changes, in order.
    perf_table: pd.Series = hist.apply(month_perf).sort_values(ascending=False)

    # make buy list of the top N stocks
    buy_list: pd.Series = perf_table.iloc[:context.stocks_to_hold]

    # the rest will not be held
    the_rest: pd.Series = perf_table.iloc[context.stocks_to_hold:]

    # place target buy orders for top N stocks
    for stock, perf in buy_list.items():
        stock_weight = 1 / context.stocks_to_hold
        # place order
        if data.can_trade(stock):
            order_target_percent(stock, stock_weight)

    # make sure we are flat the rest
    for stock, perf in the_rest.items():
        if data.can_trade(stock):
            order_target_percent(stock, 0.0)


def analyze(context, perf):
    # Use PyFolio to generate a performance report
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
    pf.create_full_tear_sheet(returns, positions=positions, transactions=transactions)


if __name__ == "__main__":
    start = pd.Timestamp("2003-01-01")
    end = pd.Timestamp("2017-12-31")

    run_algorithm(
        start=start,
        end=end,
        initialize=initialize,
        analyze=analyze,
        capital_base=10000,
        data_frequency="daily",
        bundle="quandl",
    )
