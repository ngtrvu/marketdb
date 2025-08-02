import logging
import numpy as np
import pandas as pd

from common.fear_greed_index.data_classes.stock_sense_score import (
    StockSenseScore,
)


class SenseModel:
    sense_score: StockSenseScore
    stock_df: pd.DataFrame
    volatility: float
    symbol: str
    date: str

    rsi: list
    sma: list
    stock_returns: list

    def __init__(
        self,
        symbol: str,
        stock_df: pd.DataFrame,
        sma: list,
        rsi: list,
        stock_returns: list,
        volatility: float,
        date: str = "",
    ):
        self.symbol = symbol
        self.date = date
        self.stock_df = stock_df
        self.volatility = volatility

        self.rsi = rsi
        self.sma = sma
        self.stock_returns = stock_returns

    def trendline(self, series: list, order: int = 1):
        # filter nan value in series
        series = [s for s in series if not np.isnan(s)]
        coeffs = np.polyfit(range(1, len(series) + 1), list(series), order)
        slope = coeffs[-2]
        return float(slope)

    def is_advance_by_sma(self, values, n_day=5):
        trend_ = self.trendline(values[-n_day:])
        if trend_ > 0:
            return True
        return False

    def sma_to_sense(self, values: list, n_day=5):
        trend_ = self.trendline(values[-n_day:])
        if trend_ > 0:
            return 1
        elif trend_ < 0:
            return 0
        return 0.5

    def rsi_to_sense(self, value: float):
        if value < 30:
            return 1
        elif value > 70:
            return 0
        return 0.5

    def returns_to_sense(self, returns: list, n_day=5):
        if sum(returns[-n_day:]) >= 0:
            return 1
        return 0

    def volatility_to_sense(self, value: float):
        value = abs(value)
        if value <= 0.01:
            return 1
        elif value <= 0.02:
            return 0.2
        return 0

    def get_score(self):
        return self.sense_score

    def compute(self):
        _sma = [s for s in self.sma if not np.isnan(s)]
        is_advance = self.is_advance_by_sma(_sma, n_day=5)
        _sma_sense = self.sma_to_sense(values=self.rsi, n_day=5)
        _rsi_sense = self.rsi_to_sense(value=self.rsi[-1])
        _returns_sense = self.returns_to_sense(self.stock_returns)
        _volatility_sense = self.volatility_to_sense(self.volatility)

        # logging.debug(f"_sma_sense {_sma_sense}, _rsi_sense {_rsi_sense}, "
        #               f"_returns_sense {_returns_sense}, volatility {_volatility_sense}")

        volume = self.stock_df.iloc[-1]["volume"]  # last day volume
        close = self.stock_df.iloc[-1]["close"]

        self.sense_score = StockSenseScore(
            name=self.symbol,
            date=self.date,
            price=close,
            volume=volume,
            # indicators
            returns=self.stock_returns[-1],
            is_advance=is_advance,
            volatility=self.volatility,
            sma=self.sma[-1],
            rsi=self.rsi[-1],
            # sentiment
            sma_sense=_sma_sense,
            rsi_sense=_rsi_sense,
            returns_sense=_returns_sense,
            volatility_sense=_volatility_sense,
        )

        return self.sense_score
