from datetime import timedelta

import pandas as pd

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockPriceHistoryBackfill(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    selected_fields = [
        # must have data
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "exchange",
        # # intraday data
        # "type",
        # "timestamp",
        # "reference",
        # "ceiling",
        # "floor",
        # "price",
        # "trading_value",
    ]

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.bucket_name = Config().get_bucket_name()

    def pipeline(self, input_date: str = None) -> bool:
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"StockPriceHistoryBackfill: No trading today {input_date}...")
            return True

        # # load daily stock prices on input_date
        daily_prices_df = self.load_daily_stock_prices(date_str=input_date)
        if daily_prices_df.empty:
            logger.info(
                f"StockPriceHistoryBackfill: No daily trading data is loaded on {input_date}..."
            )
            return False

        # previous_trading_date = self.get_previous_trading_date_str(date_str=input_date)
        # load the bulk stock prices on previous trading date
        bulk_adjusted_prices_df = self.load_cafef_stock_price_upto(
            date_str=input_date,
        )

        if bulk_adjusted_prices_df.empty:
            logger.error(
                f"StockPriceHistoryBackfill Error: No bulk prices OHLC is loaded upto {input_date}..."
            )
            return False
        else:
            logger.info(
                f"Loaded historical bulk prices {bulk_adjusted_prices_df.shape} upto {input_date}."
            )

        self.data_frame = pd.concat([bulk_adjusted_prices_df], ignore_index=True)

        if self.data_frame.empty:
            logger.error(
                f"StockPriceHistoryBackfill Error: No trading data to export to GCS on {input_date}..."
            )
            return False

        # convert 'date' field from timestamps to strings of date
        # self.data_frame = self.convert_timestamps_to_date_strs(self.data_frame)

        self.upload_data_frame_to_gcs(
            dataset_name="stock_price_ohlc_bulk_v3",
            date_str=input_date,
            file_name="stock_price_bulk.json",
        )

        logger.info(
            f"StockPriceHistoryBackfill on {input_date} is successfully executed..."
        )
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

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

        while not self.is_trading_date(date_str=most_recent_trading_date):
            most_recent_trading_date = self.get_yesterday_str(
                input_date=most_recent_trading_date
            )

        return most_recent_trading_date

    def convert_timestamps_to_date_strs(self, df: pd.DataFrame) -> pd.DataFrame:
        # convert integer timestamp to datetime
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        # convert UTC to Vietnam timezone
        df["date"] = df["date"].dt.tz_localize("UTC").dt.tz_convert(VN_TIMEZONE)
        # format datetime as date string
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        return df

    def transform_cafef_stock_price_bulk(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.rename(
            columns={
                "<Ticker>": "symbol",
                "<DTYYYYMMDD>": "date",
                "<Open>": "open",
                "<High>": "high",
                "<Low>": "low",
                "<Close>": "close",
                "<Volume>": "volume",
            }
        )
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.date
        df["date"] = df["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df["open"] = df['open'].apply(lambda x: round(x* 1000, 0))
        df["high"] = df['high'].apply(lambda x: round(x* 1000, 0))
        df["low"] = df['low'].apply(lambda x: round(x* 1000, 0))
        df["close"] = df['close'].apply(lambda x: round(x* 1000, 0))

        return df

    def load_cafef_stock_price_upto(self, date_str: str):
        self.new_lines = True
        df = pd.DataFrame()
        prefix = ""
        for exchange in ["HOSE", "HNX", "UPCOM"]:
            if exchange == "INDEX":
                prefix = "INDEX"
            elif exchange == "HOSE":
                prefix = "HSX"
            elif exchange == "HNX":
                prefix = "HNX"
            elif exchange == "UPCOM":
                prefix = "UPCOM"
            else:
                continue

            if not prefix:
                continue

            exchange_df = self.load_csv(
                bucket_name=Config.BUCKET_NAME,
                base_path="crawler/cafef_stock_price_upto",
                input_date=date_str,
                file_name_prefix=f"CafeF.{prefix}.Upto",
            )
            exchange_df["exchange"] = exchange
            df = pd.concat([df, exchange_df], ignore_index=True, sort=False)

        if not df.empty:
            logger.info(f"Loaded cafef stock prices on {date_str} successfully...")
            df = self.transform_cafef_stock_price_bulk(df)

            if "date" not in df.columns:
                df = self.convert_timestamps_to_date_strs(df)
            return df[self.selected_fields]

        return pd.DataFrame()

    def upload_data_frame_to_gcs(
            self,
            namespace="marketdb",
            dataset_name: str = "stock_price_ohlc_bulk_v3",
            date_str: str = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE),
            file_name: str = "stock_price_bulk.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = self.data_frame.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logger.info(
            f"Uploaded bulk prices OHLC with size {self.data_frame.shape} to GCS: {gcs_path} ..."
        )

    def load_daily_stock_prices(self, date_str: str):
        self.new_lines = True
        df = self.load(
            bucket_name=self.bucket_name,
            base_path="marketdb/stock_price_intraday",
            input_date=date_str,
            file_name_prefix="stock_price_ohlc.json",
        )
        if not df.empty:
            logger.info(f"Load daily trading data on {date_str} successfully...")
            if "date" not in df.columns:
                df = self.convert_timestamps_to_date_strs(df)
            for col in self.selected_fields:
                if col not in df.columns:
                    df[col] = None

            return df[self.selected_fields]

        return pd.DataFrame()
