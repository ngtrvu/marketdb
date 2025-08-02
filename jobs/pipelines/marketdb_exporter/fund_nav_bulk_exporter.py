import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from utils.logger import logger
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from config import Config
from common.mdb.client import MarketdbClient


class FundNavBulkExporter(MiniJobBase):

    def __init__(self):
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.marketdb_client.export_table_to_gcs(
            bucket_name=Config.BUCKET_NAME,
            dataset_name="marketdb",
            table_name="fund",
        )

        self.marketdb_client.export_table_to_gcs(
            bucket_name=Config.BUCKET_NAME,
            dataset_name="marketdb",
            table_name="fund_nav_daily",
            directory_name="fund_nav_daily_bulk",
        )

        return True
