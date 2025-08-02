import logging
from datetime import timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    date_str_reformat,
    get_date_str,
    str_to_datetime,
)
from common.tinydwh.storage.connector import GCS
from common.mdb.client import MarketdbClient
from config import Config


class StockCorporateActionJob(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    new_lines = False

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio

    def load_stock_price(self, input_date: str, selected_fields: list, drop_index: bool = False):
        df = self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_intraday",
            file_name_prefix="stock_price_ohlc.json",
        )
        if not df.empty:
            df = df[selected_fields]
            df = df.set_index("symbol", drop=drop_index)

            logging.info(f"Load stock price data on {input_date} successfully")
        return df

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        is_trading_date = MarketdbClient().check_calendar(datetime_obj)
        if not is_trading_date:
            logging.info(f"StockCorporateActionJob: No trading today: {input_date}")
            return True

        df = self.load_stock_price(
            input_date=input_date, selected_fields=["symbol", "exchange", "date", "reference"]
        )
        if df.empty:
            logging.warning(f"StockCorporateActionJob: No price data on {input_date}")
            return False

        # Load yesterday data
        self.new_lines = False
        yesterday_input_date = self.get_previous_trading_date_str(date_str=input_date)
        yesterday_df = self.load_stock_price(
            input_date=yesterday_input_date,
            selected_fields=["symbol", "close", "reference"],
            drop_index=True,
        )

        # Preprocess yesterday data before merging to today data
        yesterday_df = yesterday_df.rename(
            columns={"close": "close_1d", "reference": "reference_1d"}
        )
        df = df.join(yesterday_df, how="left", lsuffix="_left", rsuffix="_right")

        # Load stock events
        self.new_lines = True
        stock_event_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_event_log",
            file_name_prefix="stock_event_bulk.json",
        )
        stock_event_df = stock_event_df[
            [
                "symbol",
                "exright_date",
                "issue_date",
                "value",
                "ratio",
                "dividend_type",
                "event_type",
            ]
        ]
        stock_event_df = stock_event_df.set_index("symbol")
        stock_event_df = stock_event_df[
            (stock_event_df["dividend_type"].str.upper() == "STOCK")
            | (stock_event_df["dividend_type"].str.upper() == "CASH")
        ]

        stock_event_date_input = date_str_reformat(
            input_date, date_format="%Y/%m/%d", to_date_format="%Y-%m-%d"
        )
        stock_event_df = stock_event_df[
            (stock_event_df["exright_date"] == stock_event_date_input)
            & ((stock_event_df["ratio"] > 0) | (stock_event_df["value"] > 0))
        ]

        logging.info(f"stock event df {stock_event_df}")
        self.new_lines = False

        # In some cases, the stock doesn't have the volume, upcom stocks for examples. The close price is the reference
        # price (!??). However, the reference price (for upcom stock) of the next day is calculated by the last average
        # matched prices instead of the last close price.
        df["close_1d"] = np.where(df["close_1d"] > 0, df["close_1d"], df["reference_1d"])

        # keep the stocks which are changed in prices
        adjusted_df_with_upcom = df[df["close_1d"] != df["reference"]]  # including upcom

        # Given the stock event which is ground truth, we're going to join the pricing data to the event dataset.
        dividend_df: pd.DataFrame = stock_event_df.join(
            adjusted_df_with_upcom, how="left", lsuffix="_left", rsuffix="_right"
        )

        # TODO: fix price data sources, it's still not correct
        # In some cases, the stock events are not covered the stocks, we should keep in our db
        # adjusted_df_with_hose_hnx = df[(df['change_value'] != 0) & (df['exchange'] != 'upcom')]  # excluding upcom
        # dividend_df: pd.DataFrame = dividend_df.join(adjusted_df_with_hose_hnx,
        #                                              how='outer', lsuffix='_left', rsuffix='_right')

        dividend_df["dividend_type"] = dividend_df["dividend_type"].str.upper()
        dividend_df["cash"] = np.where(
            dividend_df["dividend_type"] == "CASH", dividend_df["value"], np.nan
        )
        dividend_df["stock"] = np.where(
            dividend_df["dividend_type"] == "STOCK", dividend_df["ratio"], np.nan
        )
        if "issue_date" not in dividend_df.columns:
            dividend_df["issue_date"] = None

        logging.info(f"Dividends DF:\n{dividend_df}")
        self.data_frame = dividend_df

        if dividend_df.empty:
            logging.info("StockCorporateActionJob: empty Dividends DF")
            return False

        self.export(input_date=input_date, df=dividend_df)
        logging.info(f"StockCorporateActionJob is successfully executed")
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_yesterday_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        return get_date_str(
            datetime_obj - timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_previous_trading_date_str(self, date_str: str) -> str:
        """Get the most recent previous trading date."""
        most_recent_trading_date = self.get_yesterday_str(input_date=date_str)

        while not self.is_trading_date(date_str=most_recent_trading_date):
            most_recent_trading_date = self.get_yesterday_str(input_date=most_recent_trading_date)

        return most_recent_trading_date

    def export(self, input_date: str, df: pd.DataFrame):
        gcs = GCS()

        dataset_name = "stock_corporate_actions"
        namespace = "marketdb"
        gcs_path = f"{namespace}/{dataset_name}/{input_date}/{dataset_name}.json"

        logging.info(f"Upload {gcs_path} to GCS...")
        json_data = df.to_json(orient="records", lines=True)
        gcs.upload_dict(dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path)

    def load_backfill_dates(self, input_date: str, from_date: str):
        utils = DateRangeUtils()
        datetime_obj = str_to_datetime(input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        from_date, to_date = utils.get_date_range(
            date_range=utils.DATE_RANGE_YTD, to_date=datetime_obj
        )
        return utils.get_dates_by_range(from_date, to_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
