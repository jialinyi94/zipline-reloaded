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
    X = pd.DataFrame(np.random.randn(100, 3))
    results = relative_long_short_score(X, X)
    print(results)
