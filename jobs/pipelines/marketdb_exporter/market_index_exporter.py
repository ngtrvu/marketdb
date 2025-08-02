import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.dj_exporter import DatetimeFlags
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
)
from utils.logger import logger
from common.mdb.client import MarketdbClient
from config import Config
from common.mdb.trading_calendar import TradingCalendar


class MarketIndexExporter(MiniJobBase, TradingCalendar):
    data_frame: DataFrame = pd.DataFrame()

    def __init__(self):
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logger.info(f"MarketIndexExporter: No trading today {input_date}...")
            return True

        config = Config()
        bucket_name = config.get_bucket_name()

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="market_index",
            input_date=DatetimeFlags.NO_DATETIME.value,
        )
        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="market_index_daily",
            input_date=DatetimeFlags.NO_DATETIME.value,
        )

        return True
