from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame
import os

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
    get_datetime_now,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class IndustryAnalyticsDailyJob(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    result_dfs: list = []
    sampling_ratio: float = 1.0
    marketdb_client: MarketdbClient = None

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()
        self.bucket_name = os.environ.get("BUCKET_NAME")

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"IndustryAnalyticsDailyJob: No trading today {input_date}...")
            return True

        stock_industry_df = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/industry",
        )

        if stock_industry_df.empty:
            logger.info("stock_industry_df: no data...")
            return False

        stock_info_df = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/stock",
        )

        if stock_info_df.empty:
            logger.info("stock_info_df: no data...")
            return False

        # load end of day price data by yesterday
        yesterday_input_date = self.get_previous_trading_date_str(date_str=input_date)
        yesterday_stock_price_df = self.load(
            input_date=yesterday_input_date,
            bucket_name=self.bucket_name,
            base_path=f"marketdb/stock_price_ohlc_daily",
        )

        if yesterday_stock_price_df.empty:
            logger.warning(
                f"IndustryAnalyticsDailyJob: No stock price data on {yesterday_input_date}."
            )
            return False

        stock_change_df = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/stock_price_analytics",
        )

        if stock_change_df.empty:
            logger.info("stock_change_df: no data...")
            return False

        stock_industry_df = stock_industry_df.set_index("id")
        stock_industry_df = stock_industry_df[["icb_code"]]

        stock_info_df = stock_info_df.set_index("symbol")

        # Exclude stock outstanding_shares are null or empty or equal to 0,
        stock_info_df = stock_info_df[stock_info_df["outstanding_shares"] > 0]
        stock_info_df = stock_info_df[
            [
                "outstanding_shares",
                "industry_id",
                "super_sector_id",
                "sector_id",
                "sub_sector_id",
            ]
        ]

        yesterday_stock_price_df = yesterday_stock_price_df.set_index("symbol")
        yesterday_stock_price_df = yesterday_stock_price_df[["close"]]

        stock_change_df = stock_change_df.set_index("symbol")
        stock_change_df = stock_change_df[
            [
                "price_1d",
                "price_1w",
                "price_1m",
                "price_3m",
                "price_6m",
                "price_1y",
                "price_3y",
                "price_5y",
                "price_ytd",
            ]
        ]

        merged_df = yesterday_stock_price_df.merge(
            stock_info_df, left_index=True, right_index=True
        )
        merged_df = merged_df.merge(stock_change_df, left_index=True, right_index=True)

        # build df for aggregation by industry
        df = pd.DataFrame()
        df.index = merged_df.index

        # compute historical market cap
        df["market_cap"] = merged_df["outstanding_shares"] * merged_df["close"]
        df["market_cap_1d"] = merged_df["outstanding_shares"] * merged_df["price_1d"]
        df["market_cap_1w"] = merged_df["outstanding_shares"] * merged_df["price_1w"]
        df["market_cap_1m"] = merged_df["outstanding_shares"] * merged_df["price_1m"]
        df["market_cap_3m"] = merged_df["outstanding_shares"] * merged_df["price_3m"]
        df["market_cap_6m"] = merged_df["outstanding_shares"] * merged_df["price_6m"]
        df["market_cap_1y"] = merged_df["outstanding_shares"] * merged_df["price_1y"]
        df["market_cap_3y"] = merged_df["outstanding_shares"] * merged_df["price_3y"]
        df["market_cap_5y"] = merged_df["outstanding_shares"] * merged_df["price_5y"]
        df["market_cap_ytd"] = merged_df["outstanding_shares"] * merged_df["price_ytd"]

        industry_df = df.copy()
        industry_df["id"] = pd.to_numeric(merged_df["industry_id"], downcast="integer")
        industry_df = industry_df.groupby(["id"]).sum()
        industry_df["industry_id"] = industry_df.index.astype(int)

        super_sector_df = df.copy()
        super_sector_df["id"] = pd.to_numeric(
            merged_df["super_sector_id"], downcast="integer"
        )
        super_sector_df = super_sector_df.groupby(["id"]).sum()
        super_sector_df["industry_id"] = super_sector_df.index.astype(int)

        sector_df = df.copy()
        sector_df["id"] = pd.to_numeric(merged_df["sector_id"], downcast="integer")
        sector_df = sector_df.groupby(["id"]).sum()
        sector_df["industry_id"] = sector_df.index.astype(int)

        sub_sector_df = df.copy()
        sub_sector_df["id"] = pd.to_numeric(
            merged_df["sub_sector_id"], downcast="integer"
        )
        sub_sector_df = sub_sector_df.groupby(["id"]).sum()
        sub_sector_df["industry_id"] = sub_sector_df.index.astype(int)

        industry_df = self.compute(industry_df)
        industry_df = industry_df.merge(
            stock_industry_df, left_index=True, right_index=True
        )
        industry_df["datetime"] = get_datetime_now(tz=VN_TIMEZONE)
        if not industry_df.empty:
            self.result_dfs.append(industry_df)
            self.indexing_df(industry_df.to_dict("records"))

        super_sector_df = self.compute(super_sector_df)
        super_sector_df = super_sector_df.merge(
            stock_industry_df, left_index=True, right_index=True
        )
        super_sector_df["datetime"] = get_datetime_now(tz=VN_TIMEZONE)
        if not super_sector_df.empty:
            self.result_dfs.append(super_sector_df)
            self.indexing_df(super_sector_df.to_dict("records"))

        sector_df = self.compute(sector_df)
        sector_df = sector_df.merge(
            stock_industry_df, left_index=True, right_index=True
        )
        sector_df["datetime"] = get_datetime_now(tz=VN_TIMEZONE)
        if not sector_df.empty:
            self.result_dfs.append(sector_df)
            self.indexing_df(sector_df.to_dict("records"))

        sub_sector_df = self.compute(sub_sector_df)
        sub_sector_df = sub_sector_df.merge(
            stock_industry_df, left_index=True, right_index=True
        )
        sub_sector_df["datetime"] = get_datetime_now(tz=VN_TIMEZONE)
        if not sub_sector_df.empty:
            self.result_dfs.append(sub_sector_df)
            self.indexing_df(sub_sector_df.to_dict("records"))

        logger.info(f"IndustryAnalyticsJob is successfully executed")
        return True

    def get_result_dataframe(self):
        return self.result_dfs

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return self.marketdb_client.check_calendar(datetime_obj=datetime_obj)

    def get_yesterday_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return get_date_str(
            datetime_obj - timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_previous_trading_date_str(self, date_str: str) -> str:
        """Get the most recent previous trading date."""
        most_recent_trading_date = self.get_yesterday_str(input_date=date_str)
        max_attemps = 10
        count = 0

        while True:
            count += 1
            is_trading = self.is_trading_date(date_str=most_recent_trading_date)
            if is_trading or count > max_attemps:
                break
            most_recent_trading_date = self.get_yesterday_str(
                input_date=most_recent_trading_date
            )

        return most_recent_trading_date

    def compute(self, df: pd.DataFrame):
        df["change_percentage_1d"] = np.where(
            df["market_cap_1d"] == 0,
            None,
            (df["market_cap"] - df["market_cap_1d"]) * 100 / df["market_cap_1d"],
        )
        df["change_percentage_1w"] = np.where(
            df["market_cap_1w"] == 0,
            None,
            (df["market_cap"] - df["market_cap_1w"]) * 100 / df["market_cap_1w"],
        )
        df["change_percentage_1m"] = np.where(
            df["market_cap_1m"] == 0,
            None,
            (df["market_cap"] - df["market_cap_1m"]) * 100 / df["market_cap_1m"],
        )
        df["change_percentage_3m"] = np.where(
            df["market_cap_3m"] == 0,
            None,
            (df["market_cap"] - df["market_cap_3m"]) * 100 / df["market_cap_3m"],
        )
        df["change_percentage_6m"] = np.where(
            df["market_cap_6m"] == 0,
            None,
            (df["market_cap"] - df["market_cap_6m"]) * 100 / df["market_cap_6m"],
        )
        df["change_percentage_1y"] = np.where(
            df["market_cap_1y"] == 0,
            None,
            (df["market_cap"] - df["market_cap_1y"]) * 100 / df["market_cap_1y"],
        )
        df["change_percentage_3y"] = np.where(
            df["market_cap_3y"] == 0,
            None,
            (df["market_cap"] - df["market_cap_3y"]) * 100 / df["market_cap_3y"],
        )
        df["change_percentage_5y"] = np.where(
            df["market_cap_5y"] == 0,
            None,
            (df["market_cap"] - df["market_cap_5y"]) * 100 / df["market_cap_5y"],
        )
        df["change_percentage_ytd"] = np.where(
            df["market_cap_ytd"] == 0,
            None,
            (df["market_cap"] - df["market_cap_ytd"]) * 100 / df["market_cap_ytd"],
        )

        return df

    def indexing_df(self, items: list[dict]) -> bool:
        try:
            logger.debug(f"Indexing items: {items}")
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="IndustryAnalytics",
                key_fields=["industry_id"],
                payload=items,
            )
            logger.debug(f"Indexing response: {response}")
            return success, response
        except Exception as ex:
            logger.error(f"Error indexing: {ex}")
            return False, response
