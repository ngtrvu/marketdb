import logging
import os

import pandas as pd
from django.db import connection
from google.cloud import storage
from pandas import DataFrame

from utils.logger import logger
from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from config import Config
from common.mdb.trading_calendar import TradingCalendar
from common.mdb.client import MarketdbClient


class StockEventBulkExporter(MiniJobBase, TradingCalendar):

    def __init__(self):
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logger.info(f"StockEventBulkExporter: No trading today {input_date}...")
            return True

        config = Config()
        bucket_name = config.get_bucket_name()

        self.marketdb_client.export_table_to_gcs(
            bucket_name=bucket_name,
            dataset_name="marketdb",
            table_name="stock_event_log",
        )
        return True
