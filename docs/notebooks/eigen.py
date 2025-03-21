import numpy as np
import pandas as pd
import statsmodels.api as sm
import sklearn.linear_model as lm


def ar1(ts: pd.Series):
    X = sm.add_constant(ts.shift(1).dropna())
    y = ts.iloc[1:]
    model = sm.OLS(y, X)
    results = model.fit()
    a: float = results.params.iloc[0]
    b: float = results.params.iloc[1]
    var: float = results.mse_resid
    return a, b, var


def s_scores(
    residuals: pd.DataFrame,
    lookback: int,
    center: bool,
):
    results = [
        ar1(residuals[col]) for col in residuals.columns
    ]
    df_results = pd.DataFrame(results, columns=["a", "b", "var"], index=residuals.columns)

    df_results = df_results.loc[
        (df_results["b"] < np.exp(-2 / lookback))
        & (df_results["b"] > 0)
    ]

    a = df_results["a"]
    b = df_results["b"]
    var = df_results["var"]

    tmp = ((1 - b**2) / var) ** 0.5

    m = a / (1 - b)

    s = - m * tmp

    if center:
        s += m.mean() * tmp

    return s


def relative_long_short_score(
    targets: pd.DataFrame,
    features: pd.DataFrame,
    lookback: int = 60,
    center: bool = True,
):
    model = lm.LinearRegression(fit_intercept=True)
    model.fit(features.values, targets.values)
    residuals = pd.DataFrame(
        targets.values - model.predict(features.values),
        columns=targets.columns,
        index=targets.index
    )
    return s_scores(residuals, lookback=lookback, center=center)


if __name__ == "__main__":
    import os
    path_to_folder = os.path.expanduser("~/.data/test/daily")
    tickers = ["AAPL", "IBM", "BA", "^DJI"]
    all_df = []
    for ticker in tickers:
        path_to_file = os.path.join(path_to_folder, f"{ticker}.csv")
        df = pd.read_csv(path_to_file, index_col=0)
        all_df.append(df["close"])
    all_df = pd.concat(all_df, axis=1, keys=tickers)
    df_returns = all_df.pct_change().dropna()

    scores = []
    for window in df_returns.rolling(window=60, min_periods=60):
        if window.shape[0] < 60:
            continue
        features = window.iloc[:, -1:]
        targets = window.iloc[:, :-1]
        s = relative_long_short_score(targets, features)
        scores.append(s)
    scores = pd.concat(scores, axis=1).T
    print(scores)
