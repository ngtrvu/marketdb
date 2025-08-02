import pandas as pd


def compute_nav_change_rate(present_value: float, initial_value: float) -> float:
    if present_value is None or initial_value is None:
        return None

    if initial_value == 0.0:
        return None

    return (present_value - initial_value) / initial_value


def compute_nav_annualized_return(change_rate: float, n_year: int) -> float:
    if not change_rate:
        return None

    return (1 + change_rate) ** (1/n_year) - 1


def compute_maximum_drawdown(nav_series: pd.Series) -> float:
    returns = nav_series.pct_change(1)
    cum_rets = (1 + returns).cumprod() - 1
    nav = ((1 + cum_rets) * 100).fillna(100)
    hwm = nav.cummax()
    dd = nav / hwm - 1

    return min(dd)
