import json
import os
from datetime import timedelta, datetime

import pandas as pd
import pytz
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    ensure_tzaware_datetime,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger, setup_logger
from common.fear_greed_index.constants import VN100
from common.fear_greed_index.fear_greed_score_v2 import (
    FearGreedScoreV2,
)
from common.tinydwh.storage.connector import GCS
from common.mdb.client import MarketdbClient
from common.mdb.trading_calendar import TradingCalendar
from config import Config

setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))


class FearGreedIndexComputingJob(MiniJobBase, TradingCalendar):
    """
    This is for one off load collection data from stockdb
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    new_lines = True
    parallel = 1

    def __init__(self, sampling_ratio: float = 1.0):
        super().__init__()
        self.market_df: pd.DataFrame = pd.DataFrame()
        self.vn_stocks: pd.DataFrame = pd.DataFrame()
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logger.info(f"FearGreedIndexComputingJob: No trading today {input_date}...")
            return False

        # Load data
        self.load_data(input_date=input_date)
        if self.vn_stocks.empty:
            logger.error(f"The Stock data is empty on {input_date}...")
            return False

        if self.market_df.empty or self.vn_stocks.empty:
            logger.error(f"The Market index is empty on {input_date}...")
            return False

        fear_greed_index_score = self.compute(input_date=input_date)
        self.upload_to_gcs(json_data=fear_greed_index_score, input_date=input_date)
        return True

    def __load_stock_price(self, input_date: str, selected_fields: list):
        df = self.load(
            base_path="marketdb/stock_price_ohlc_250_days_vn100",
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            file_name_prefix="stock_price_bulk.json",
        )

        if not df.empty:
            df = df[selected_fields]
            df = df.set_index("symbol", drop=False)

            logger.info(f"Load stock price data on {input_date} successfully")
        return df

    def load_data(self, input_date):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        logger.info("Loading VN100 stocks data...")
        selected_fields = ["symbol", "date", "open", "high", "low", "close", "volume"]

        if self.vn_stocks.empty:
            # Load historical data from previous trading date
            historical_df: pd.DataFrame()
            previous_trading_date = self.get_previous_trading_date(input_date=input_date)
            historical_df = self.__load_stock_price(
                input_date=previous_trading_date, selected_fields=selected_fields
            )
            if historical_df.empty:
                logger.error(
                    f"FearGreedIndexComputingJob Error: No historical trading data is loaded on "
                    f"{previous_trading_date}..."
                )
                return False

            current_df = self.load(
                input_date=input_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="marketdb/stock_price_intraday",
                file_name_prefix="stock_price_ohlc.json",
            )
            if current_df.empty:
                logger.error(
                    f"FearGreedIndexComputingJob Error: No indices data is loaded on "
                    f"{input_date}..."
                )
                return False

            current_df["date"] = current_df["timestamp"].apply(lambda x: x.date())
            current_df = current_df[selected_fields]

            if not current_df.empty:
                # merge with realtime/intraday stock price for current score
                current_df = current_df[
                    current_df["symbol"].isin(historical_df["symbol"].unique())
                ]
                self.vn_stocks = pd.concat([historical_df, current_df])
            else:
                raise Exception(
                    "The current price data is empty. Make sure that you've loaded all data"
                )

            # self.vn_stocks = self.vn_stocks[self.vn_stocks['symbol'].isin(VN30)]
            self.vn_stocks = self.vn_stocks[self.vn_stocks["symbol"].isin(VN100)]
        
        if self.market_df.empty:
            logger.info("Loading VN Market Index data...")
            history_df = self.load(
                input_date=previous_trading_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="marketdb/market_index_ohlc_bulk",
                file_name_prefix="market_index_ohlc_bulk.json",
            )
            if history_df.empty:
                logger.error(
                    f"FearGreedIndexComputingJob Error: No historical market index data is loaded on "
                    f"{previous_trading_date}..."
                )
                return False

            logger.info(f"Loading VN Market Index intraday {input_date}...")
            intraday = self.load(
                input_date=input_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="marketdb/market_index_ohlc",
                file_name_prefix="market_index_ohlc.json",
            )
            if intraday.empty:
                logger.error(
                    f"FearGreedIndexComputingJob Error: No intraday market index data is loaded on "
                    f"{input_date}..."
                )
                return False

            intraday["date"] = intraday["timestamp"].apply(
                lambda x: pd.to_datetime(x, format="%Y-%m-%d") if x else ""
            )
            intraday["volume"] = intraday["totalVolume"]
            intraday["high"] = intraday["close"]
            intraday["low"] = intraday["close"]
            intraday["date"] = intraday["date"].apply(
                lambda x: pd.to_datetime(x, format="%Y-%m-%d") if x else ""
            )
            history_df = history_df[selected_fields]
            intraday = intraday[selected_fields]

            self.market_df = pd.concat([history_df, intraday])
            self.market_df = self.market_df[selected_fields]
            # we use VNINDEX for now, the whole market indicator
            self.market_df = self.market_df[self.market_df["symbol"] == "VNINDEX"]
            self.market_df = self.market_df.sort_values("date")
            self.market_df = self.market_df[
                self.market_df["date"] <= input_date.replace("/", "-")
            ]

            self.market_df = self.transform_market_ohlc_bulk(
                self.market_df[self.market_df["volume"] > 0]
            )

    def transform_market_ohlc_bulk(self, ohlc: pd.DataFrame):
        market_df = pd.DataFrame()
        market_df["open"] = ohlc["open"].apply(float)
        market_df["high"] = ohlc["high"].apply(float)
        market_df["low"] = ohlc["low"].apply(float)
        market_df["close"] = ohlc["close"].apply(float)
        market_df["volume"] = ohlc["volume"].apply(float)
        market_df["datetime"] = pd.to_datetime(ohlc["date"], format="%Y-%m-%d")
        market_df["date"] = market_df["datetime"].apply(lambda x: x.date())
        market_df.index = pd.to_datetime(market_df["datetime"], format="%Y-%m-%d")
        market_df.sort_index(inplace=True)
        market_df.drop_duplicates(subset="datetime", inplace=True)

        market_df["change"] = market_df["close"].diff()
        market_df["pct_change"] = market_df["close"].pct_change()

        return market_df

    def compute(self, input_date, date_format="%Y/%m/%d") -> dict:
        logger.info(f"Compute FGI score & market indicators on {input_date}...")

        datetime_obj = str_to_datetime(input_date, date_format, tz=VN_TIMEZONE)
        current_time = datetime.now().time()
        # Combine the date from datetime_obj with the current time
        combined_datetime = pytz.timezone(VN_TIMEZONE).localize(
            datetime.combine(datetime_obj.date(), current_time)
        )

        # compute scores using FearGreedScore analytic model
        analytic_model = FearGreedScoreV2()
        market_indicators = analytic_model.compute_market(
            self.market_df, input_date=input_date
        )
        fear_greed_score, success = analytic_model.compute(
            stocks_df=self.vn_stocks, input_date=input_date
        )
        if success:
            fear_greed_index_score = {
                "date": datetime_obj.strftime("%Y-%m-%d"),
                "datetime": combined_datetime.isoformat(),
                "fear_greed_score": fear_greed_score,
                "market_indicators": market_indicators,
            }
            logger.info(f"fear_greed_index_score {fear_greed_index_score}")

            return fear_greed_index_score

        return {}

    def upload_to_gcs(self, json_data, input_date):
        gcs = GCS()
        gcs_path = f"analytics/fear_greed_index/{input_date}/fear_greed_index.json"

        logger.info(f"Upload {gcs_path} to GCS...")
        gcs.upload_dict(
            dict_json=json.dumps(json_data),
            bucket_name=Config.BUCKET_NAME,
            gcs_path=gcs_path,
        )

    def load_backfill_dates(self, to_date, from_date):
        range_utils = DateRangeUtils()
        from_date = str_to_datetime(
            input_str=from_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        to_date = str_to_datetime(
            input_str=to_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        dates = range_utils.get_dates_by_range(from_date, to_date)

        backfill_dates = [d.strftime("%Y/%m/%d") for d in dates]

        logger.info(f"All backfill dates {backfill_dates}")

        return backfill_dates
