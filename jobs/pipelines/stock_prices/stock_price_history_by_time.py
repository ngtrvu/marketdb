import os
import pandas as pd

from datetime import timezone

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    get_datetime_from_timestamp,
    str_to_datetime,
)
from utils.logger import logger, setup_logger
from common.fear_greed_index.constants import VN100
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config

setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))


class StockPriceHistoryByTime(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio

    def pipeline(self, input_date: str = None) -> bool:
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"StockPriceHistoryByTime: No trading today {input_date}...")
            return True

        # load the bulk stock prices on input_date
        base_path = "marketdb/stock_price_ohlc_bulk_v3"
        self.new_lines = True
        bulk_prices_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path=base_path,
            input_date=input_date,
        )

        if bulk_prices_df.empty:
            logger.error(
                f"StockPriceHistoryByTime Error: No bulk prices OHLC is loaded on {input_date}..."
            )
            return False
        else:
            if "date" not in bulk_prices_df.columns:
                bulk_prices_df["date"] = bulk_prices_df["timestamp"].apply(
                    lambda ts: get_datetime_from_timestamp(ts, tz=timezone(VN_TIMEZONE))
                )
                self.data_frame = bulk_prices_df

            logger.info(
                f"Loaded historical bulk prices with size {bulk_prices_df.shape} on {input_date}."
            )

        # extract and upload the latest 250-day bulk prices of the symbols in the list VN100
        self.upload_stock_price_ohlc_vn100(date_str=input_date)

        # extract and upload adjusted yearly OHLC prices
        # self.upload_stock_price_ohlc_yearly()

        # extract and upload adjusted bulk prices OHLC of each symbol
        # self.upload_stock_price_ohlc()

        # extract and upload adjusted daily OHLC prices
        self.upload_stock_price_ohlc_daily()

        logger.info(
            f"StockPriceHistoryByTime on {input_date} is successfully executed..."
        )
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def upload_stock_price_ohlc_daily(self):
        """Upload adjusted daily bulk prices OHLC of all symbols"""
        bulk_price_grouped_by_date_df = self.data_frame.groupby(by=["date"])
        logger.info(
            f"Uploading {len(bulk_price_grouped_by_date_df)} daily bulk prices OHLC to GCS..."
        )
        for dt, group_df in bulk_price_grouped_by_date_df:
            date_str = dt[0].date().strftime("%Y/%m/%d")
            self.upload_data_to_gcs(
                df=group_df,
                dataset_name="stock_price_ohlc_daily",
                date_str=date_str,
                file_name="stock_price_ohlc_daily.json",
            )

    def upload_stock_price_ohlc_yearly(self):
        """Upload adjusted yearly bulk prices OHLC of all symbols"""
        bulk_price_grouped_by_year_df = self.data_frame.groupby(
            by=self.data_frame["date"].dt.year
        )
        logger.info(
            f"Uploading {len(bulk_price_grouped_by_year_df)} yearly bulk prices OHLC to GCS..."
        )
        for year, group_df in bulk_price_grouped_by_year_df:
            self.upload_data_to_gcs(
                df=group_df,
                dataset_name="stock_price_ohlc_yearly",
                date_str=str(year),
                file_name="stock_price_ohlc_yearly.json",
            )

    def upload_stock_price_ohlc(self):
        """Upload adjusted bulk prices OHLC of each symbol"""
        gcs = GCS()
        namespace = "marketdb"
        dataset_name = "stock_price_ohlc"

        bulk_price_grouped_by_symbol_df = self.data_frame.groupby(
            by=self.data_frame["symbol"]
        )
        logger.info(
            f"Uploading {len(bulk_price_grouped_by_symbol_df)} bulk prices OHLC by symbol to GCS..."
        )
        for symbol, group_df in bulk_price_grouped_by_symbol_df:
            gcs_path = f"{namespace}/{dataset_name}/{symbol}.json"
            json_data = group_df.to_json(orient="records", lines=True)
            gcs.upload_dict(
                dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
            )

    def upload_stock_price_ohlc_vn100(self, date_str: str, n_year=4):
        # extract and upload the latest 250-day * n_year OHLC bulk prices in the list VN100
        latest_250_dates = (
            self.data_frame["date"]
            .drop_duplicates()
            .sort_values(ascending=False)[0:250*n_year]
        )
        vn100_bulk_price_250_days_df = self.data_frame.query(
            "symbol in @VN100 and date in @latest_250_dates"
        )
        logger.info(
            f"Uploading {len(vn100_bulk_price_250_days_df.index)} bulk prices OHLC 250 days in VN100 to GCS..."
        )
        self.upload_data_to_gcs(
            df=vn100_bulk_price_250_days_df,
            dataset_name="stock_price_ohlc_250_days_vn100",
            date_str=date_str,
        )

    def upload_data_to_gcs(
        self,
        df: pd.DataFrame,
        namespace="marketdb",
        dataset_name: str = "stock_price_ohlc_250_days_vn100",
        date_str: str = get_date_str(
            date_format="%Y/%m/%d", tz=VN_TIMEZONE
        ),  # current date
        file_name: str = "stock_price_bulk.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = df.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )
