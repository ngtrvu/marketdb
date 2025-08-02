import pandas as pd
from pandas import DataFrame

from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
)
from utils.logger import logger
from common.mdb.client import MarketdbClient
from common.mdb.job import MarketDbJob
from config import Config


class StockExporter(MarketDbJob):
    data_frame: DataFrame = pd.DataFrame()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logger.info(f"StockExporter: No trading today {input_date}...")
            return True

        config = Config()
        bucket_name = config.get_bucket_name()

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="industry",
            input_date=input_date,
        )

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="stock",
            input_date=input_date,
        )

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="etf",
            input_date=input_date,
        )

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="stock_price_chart",
            input_date=input_date,
        )

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="stock_price_analytics",
            input_date=input_date,
        )

        return True
