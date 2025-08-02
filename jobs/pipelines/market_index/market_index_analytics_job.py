import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import timedelta

from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    get_datetime_now,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config
from common.mdb.trading_calendar import TradingCalendar


class MarketIndexAnalyticsJob(MiniJobBase, TradingCalendar):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date=input_date):
            logger.info(f"MarketIndexAnalyticsJob: No trading today {input_date}...")
            return True

        previous_input_date = self.get_previous_trading_date(input_date=input_date)
        market_index_df = self.load(
            input_date=previous_input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/market_index_ohlc_bulk",
        )

        if market_index_df.empty:
            raise Exception("Market Index data is empty")

        symbols = market_index_df["symbol"].unique()
        market_index_df = market_index_df[["symbol", "date", "close"]]
        market_index_analytics_df = pd.DataFrame()

        for symbol in symbols:
            df = market_index_df[market_index_df["symbol"] == symbol].sort_values(
                by=["date"], ascending=False
            )
            today_index = df.iloc[0]

            close_1d, change_1d, change_percentage_1d = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_1D,
                input_date=input_date,
            )
            close_1w, change_1w, change_percentage_1w = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_1W,
                input_date=input_date,
            )
            close_1m, change_1m, change_percentage_1m = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_1M,
                input_date=input_date,
            )
            close_3m, change_3m, change_percentage_3m = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_3M,
                input_date=input_date,
            )
            close_6m, change_6m, change_percentage_6m = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_6M,
                input_date=input_date,
            )
            close_1y, change_1y, change_percentage_1y = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_1Y,
                input_date=input_date,
            )
            close_3y, change_3y, change_percentage_3y = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_3Y,
                input_date=input_date,
            )
            close_5y, change_5y, change_percentage_5y = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_5Y,
                input_date=input_date,
            )
            close_ytd, change_ytd, change_percentage_ytd = self.compute(
                df=df,
                today_index=today_index,
                date_range=DateRangeUtils.DATE_RANGE_YTD,
                input_date=input_date,
            )

            row = {
                "symbol": symbol,
                "close": today_index["close"],
                "close_1d": close_1d,
                "change_1d": change_1d,
                "change_percentage_1d": change_percentage_1d,
                "close_1w": close_1w,
                "change_1w": change_1w,
                "change_percentage_1w": change_percentage_1w,
                "close_1m": close_1m,
                "change_1m": change_1m,
                "change_percentage_1m": change_percentage_1m,
                "close_3m": close_3m,
                "change_3m": change_3m,
                "change_percentage_3m": change_percentage_3m,
                "close_6m": close_6m,
                "change_6m": change_6m,
                "change_percentage_6m": change_percentage_6m,
                "close_1y": close_1y,
                "change_1y": change_1y,
                "change_percentage_1y": change_percentage_1y,
                "close_3y": close_3y,
                "change_3y": change_3y,
                "change_percentage_3y": change_percentage_3y,
                "close_5y": close_5y,
                "change_5y": change_5y,
                "change_percentage_5y": change_percentage_5y,
                "close_ytd": close_ytd,
                "change_ytd": change_ytd,
                "change_percentage_ytd": change_percentage_ytd,
            }
            market_index_analytics_df = pd.concat(
                [market_index_analytics_df, pd.DataFrame(row, index=["symbol"])]
            )

        # index to db
        market_index_analytics_df["datetime"] = get_datetime_now(tz=VN_TIMEZONE)
        market_index_analytics_df = market_index_analytics_df.replace({np.nan: None})

        success = self.do_indexing(market_index_analytics_df.to_dict("records"))
        if not success:
            logger.error("MarketIndexAnalyticsJob: Indexing failed.")
            return False

        logger.info(f"MarketIndexAnalyticsJob is successfully executed.")
        return True

    def get_row_by_date_range(self, df: pd.DataFrame, date_range: str, input_date: str):
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        from_date, to_date = DateRangeUtils().get_date_range_as_string(
            date_range=date_range,
            to_date=datetime_obj.date(),
            date_format="%Y-%m-%d",
            tz=VN_TIMEZONE,
        )
        date_range_df = df[df["date"] <= from_date]

        if not date_range_df.empty:
            return date_range_df.iloc[0]
        return None

    def compute(self, df: pd.DataFrame, today_index, date_range: str, input_date: str):
        row = self.get_row_by_date_range(
            df=df,
            date_range=date_range,
            input_date=input_date,
        )
        if row is not None and not row.empty:
            value_change = today_index["close"] - row["close"]
            return row["close"], value_change, (value_change * 100) / row["close"]
        return None, None, None

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="MarketIndexAnalytics",
                key_fields=["symbol"],
                payload=items,
            )
            if not success:
                logger.error(f"Error indexing: {response}")
                return False
            
            logger.info(f"Indexing {len(items)} items to table MarketIndexAnalytics successfully.")
            return True

        except Exception as ex:
            logger.error(f"Error indexing: {ex}")
            return False
