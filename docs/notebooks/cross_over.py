# define typing hints
from typing import Any
from zipline.protocol import BarData
# import zipline functions
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol
# import date and time zone libraries
from datetime import datetime
import pytz
# import visualization
import matplotlib.pyplot as plt


ZiplineContext = Any


def initialize(context: ZiplineContext):
    """
    Executed before the backtest starts.
    Set parameters and preparation.
    """
    # which stock to trade
    context.stock = symbol("AAPL")
    # moving average window
    context.index_average_window = 100

def handle_data(context: ZiplineContext, data: BarData):
    """
    Request history for the stock
    """
    equity_hist = data.history(
        assets=context.stock, 
        fields="close", 
        bar_count=context.index_average_window,
        frequency='1d'
    )
