import logging
import numpy as np
import pandas as pd
from datetime import datetime

from common.tinydwh.datetime_util import str_to_datetime, VN_TIMEZONE
from common.fear_greed_index.constants import (
    INDEX_CLOSE,
    INDEX_PCT_CHANGE,
    INDEX_DIFF,
)
from common.fear_greed_index.sense_model import SenseModel
from common.fear_greed_index.data_classes.stock_sense_score import (
    StockSenseScore,
)


class FearGreedScoreV2:
    market_data_period = 250  # days
    volatility_period = 50  # days
    momentum_period = 125  # days

    def __init__(self):
        pass

    def compute_sma(self, ticker_ds: pd.Series, n_day: int) -> list:
        if n_day > len(ticker_ds):
            n_day = len(ticker_ds)

        return ticker_ds.rolling(n_day).mean().to_list()

    def compute_stock_return(self, ticker_ds: pd.Series) -> list:
        ds = (ticker_ds / ticker_ds.shift(1)) - 1
        return ds.to_list()

    def compute_rsi(self, ticker_ds: pd.Series, n_day: int) -> list:
        delta = ticker_ds[-n_day:].diff()

        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=n_day - 1, adjust=False).mean()
        ema_down = down.ewm(com=n_day - 1, adjust=False).mean()

        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))

        # Skip first 14 days to have real values
        # ticker_df = ticker_df.iloc[n_day:]

        return rsi.to_list()

    def compute_volatility(self, ticker_ds: pd.Series, n_day: int) -> (float, float):
        if n_day > len(ticker_ds):
            n_day = len(ticker_ds)

        returns = ticker_ds / ticker_ds.shift(1)
        log_returns = np.log(returns)
        std = np.std(log_returns)

        # noted: if annually n_day will be 252 trading day, weekly is 5, monthly is 21
        volatility = std * n_day**0.5

        if np.isnan(volatility):
            volatility, std = 0.0, 0.0

        return volatility, std

    def compute_stock(self, symbol: str, stock_df: pd.DataFrame) -> StockSenseScore:
        """Compute sentiment score for each symbol

        :param stock_df: df of ohlc + volume of a given symbol
        :param symbol: stock symbol, adding metadata to dataclass
        :return:
        """
        df = stock_df.copy()
        df.rename(
            columns={
                "open_price": "open",
                "low_price": "low",
                "high_price": "high",
                "close_price": "close",
            },
            inplace=True,
        )
        df.sort_index(inplace=True)

        volatility, std = self.compute_volatility(
            ticker_ds=df["close"], n_day=self.volatility_period
        )
        logging.debug(f"n day history {len(df)} volatility {volatility}, std {std}")

        sma = self.compute_sma(ticker_ds=df["open"], n_day=20)
        rsi = self.compute_rsi(ticker_ds=df["close"], n_day=5)
        stock_returns = self.compute_stock_return(ticker_ds=df["close"])

        sense_model = SenseModel(
            symbol=symbol,
            date=df.iloc[-1].index,
            stock_df=df,
            sma=sma,
            rsi=rsi,
            stock_returns=stock_returns,
            volatility=volatility,
        )
        sense_model.compute()
        return sense_model.get_score()

    def compute_market(
        self, market_df: pd.DataFrame, input_date: str, n_market_day: int = 250
    ):
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

        logging.debug("market_df %s" % len(market_df))

        market_df = market_df[market_df.index <= datetime_obj.strftime("%Y-%m-%d")]

        # TODO: upgrade to Cboe Volatility Index (VIX)
        # TODO: refactor market volatility code, really bad code
        market_volatility_list = []
        for i in range(len(market_df)):
            if i == (len(market_df) - 1):
                market_volatility = market_volatility_list[i - 1]
            elif i == 0:
                market_volatility, _ = self.compute_volatility(
                    ticker_ds=market_df["close"],
                    n_day=self.volatility_period,
                )
            else:
                market_volatility, _ = self.compute_volatility(
                    ticker_ds=market_df.iloc[:-i]["close"],
                    n_day=self.volatility_period,
                )
            market_volatility_list.append(market_volatility)

        # first is old date, last is newest, so reverse to make it an increasing time-series
        market_volatility_list.reverse()

        # use direct value of market move
        market_diff = market_df[INDEX_PCT_CHANGE].to_list()

        market_volatility = market_diff
        market_df["volatility"] = market_volatility

        market_volatility_sma = self.compute_sma(
            ticker_ds=market_df["volatility"], n_day=50
        )
        market_df["volatility_sma"] = market_volatility_sma

        market_df = market_df.iloc[-n_market_day:]

        # compute market values
        market_value = market_df[INDEX_CLOSE].to_list()
        market_move = market_df[INDEX_DIFF].to_list()

        market_sma = self.compute_sma(
            ticker_ds=market_df["close"], n_day=self.momentum_period
        )
        market_rsi = self.compute_rsi(
            ticker_ds=market_df["close"], n_day=self.momentum_period
        )

        # TODO: add validation feature instead of adhoc check
        # print(f"market_sma[-1] {market_sma[-1]}")
        # if market_sma[-1] <= 0:
        #     exit(0)

        market_momentum_sense = (
            round((market_value[-1] - market_sma[-1]) / market_value[-1], 2) * 100
        )
        market_diff_sense = self.__get_market_diff_sense(market_diff[-1])

        market_indicators = {
            "market_index": market_value[-1],
            "market_index_previous": market_value[-2],
            "market_rsi": market_rsi[-1],
            "market_diff": market_diff[-1],
            "price_strength": (market_rsi[-1] - market_rsi[-2]) / market_rsi[-1] * 100,
            "momentum": market_sma[-1],
            "momentum_diff": market_momentum_sense,
            "market_volatility": market_volatility[-1],
            "market_volatility_sma": market_volatility_sma[-1],
        }

        return market_indicators

    def compute_sense_scores(
        self, stocks_df: pd.DataFrame, datetime_obj: datetime, n_market_day: int = 250
    ):
        """
        TODO: Refactor this, keep related stuff, the others need to move to the job pipeline
        :param datetime_obj:
        :param stocks:
        :param n_market_day:
        :return:
        """
        stock_sense_scores = []
        latest_day_data = None
        stocks_df.index = pd.to_datetime(stocks_df["date"])
        symbols = [s for s in stocks_df["symbol"].unique() if len(s) == 3]
        for symbol in symbols:
            # tmp_df = pd.DataFrame.from_dict(stocks.get(stock), orient="index")
            tmp_df = stocks_df[stocks_df["symbol"] == symbol]
            tmp_df = tmp_df[tmp_df.index <= datetime_obj.strftime("%Y-%m-%d")]

            if len(tmp_df) < n_market_day or len(tmp_df) <= 1:
                continue

            try:
                tmp_df.sort_index(inplace=True)
                stock_sense_scores.append(
                    self.compute_stock(symbol=symbol, stock_df=tmp_df)
                )

                if not latest_day_data:
                    latest_day_data = tmp_df.index[-1]
            except Exception as e:
                logging.warning(
                    f"Compute sentiment score for {symbol} data is failed: {e}"
                )

        return stock_sense_scores

    def compute_fear_greed_score(
        self, stock_sense_scores: list[StockSenseScore], datetime_obj: datetime
    ) -> dict:
        """
        A version better than dummy

        Stock Price Momentum: The VN30 Index versus its 125-day moving average
        Stock Price Breadth: The volume of shares trading in stocks on the rise versus those declining.
        Stock Price Strength: The number of stocks hitting 52-week highs and lows on the VN30
        Market Volatility: The VIX (VIX), which measures market_volatility (N/A - TBD)
        """
        momentum_senses, rsi_senses, returns_senses, volatility_senses = [], [], [], []
        ad_sense = []
        volatility = []
        advance_volume = 0
        decline_volume = 0
        rsi_high_count = 0
        rsi_low_count = 0

        price_breadth_advance = 0
        price_breadth_decline = 0

        if not len(stock_sense_scores):
            logging.error(f"stock_sense_scores is empty on date: {datetime_obj}")
            return {}

        logging.debug(f"stock_sense_scores {len(stock_sense_scores)}")

        # Compute fear index score from selected stocks' sentiment scores
        for sense_score in stock_sense_scores:
            momentum_senses.append(sense_score.sma_sense)

            # price strength
            rsi_senses.append(sense_score.rsi_sense)
            returns_senses.append(sense_score.returns_sense)
            volatility_senses.append(sense_score.volatility_sense)

            volatility.append(sense_score.volatility)
            # other computation
            advance_volume += sense_score.volume if sense_score.is_advance else 0
            decline_volume += sense_score.volume if not sense_score.is_advance else 0

            rsi_high_count += 1 if sense_score.rsi_sense >= 0.5 else 0
            rsi_low_count += 1 if sense_score.rsi_sense < 0.5 else 0

            # price breadth
            price_breadth_advance += sense_score.volume if sense_score.is_advance else 0
            price_breadth_decline += (
                sense_score.volume if not sense_score.is_advance else 0
            )
            ad_sense.append(1 if sense_score.is_advance else 0)

        if rsi_high_count == 0:
            rsi_high_count = 1

        price_strength_score = (rsi_high_count - rsi_low_count) / (
            rsi_high_count + rsi_low_count
        )
        if (price_breadth_advance + price_breadth_decline) != 0:
            price_breadth = (price_breadth_advance - price_breadth_decline) / (
                price_breadth_advance + price_breadth_decline
            )
        else:
            price_breadth = 0

        # price_breadth = sum(ad_sense)
        sentiment_df = pd.DataFrame()
        # sentiment_df.index = tickers
        # sentiment_df['momentum_sense'] = momentum_sense  # TODO: check this
        sentiment_df["rsi_sense"] = rsi_senses  # this make our score too neutral
        sentiment_df["price_breadth_sense"] = 0.0 if price_breadth < 0 else 1
        sentiment_df["returns_sense"] = returns_senses
        # sentiment_df['volatility_sense'] = volatility_sense
        sentiment_df["ad_sense"] = ad_sense
        sentiment_df["volatility"] = volatility
        # sentiment_df['market_momentum_sense'] = 0.0 if market_momentum_sense < 0 else 1  # TODO: check this
        # sentiment_df['market_diff_sense'] = market_diff_sense
        # print(sentiment_df.head())

        # Compute Fear Greed Index Score
        fear_greed_score = 0
        n_factor = 0
        n_stocks = len(stock_sense_scores)
        for factor in sentiment_df.columns:
            if "_sense" in factor:
                factor_sum = len(sentiment_df[factor].to_list())
                factor_weight = (
                    (sum(sentiment_df[factor].to_list()) / factor_sum)
                    if factor_sum > 0
                    else 0
                )
                fear_greed_score += factor_weight
                n_factor += 1

        # scale score to 0-100 range
        fear_greed_score = int(fear_greed_score * 100 / n_factor)
        logging.debug(
            f"compute_fear_greed_score {fear_greed_score} n_factor {n_factor}"
        )

        return {
            "fear_greed_score": fear_greed_score,
            "price_strength_score": price_strength_score,
            "price_breadth": price_breadth,
            "price_breadth_diff": sum(sentiment_df["ad_sense"]) / n_stocks
            if n_stocks
            else None,
        }

    def __get_market_diff_sense(self, market_diff):
        if abs(market_diff >= 0.01):
            return 0.25
        else:
            return 0.75

    def compute(self, stocks_df: pd.DataFrame, input_date: str) -> (dict, bool):
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        stock_sense_scores: list[StockSenseScore] = self.compute_sense_scores(
            stocks_df, datetime_obj
        )
        score = self.compute_fear_greed_score(stock_sense_scores, datetime_obj)
        if "fear_greed_score" not in score:
            return {}, False
        return score, True
