import logging

from marketdb.src.marketdb_django.wsgi import application

logging.info(f"Loaded django {application}")

import unittest
from unittest.mock import patch

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stocks.stock_new_initializer import (
    StockNewInitializer,
)


class StockNewInitializerTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/stocks"

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    @patch(
        "common.mdb.client.MarketdbClient.get_stock_items"
    )
    @patch(
        "common.mdb.client.MarketdbClient.get_etf_items"
    )
    def test_stock_info_initializer_job_success(
        self, etf_values, stock_values, check_calendar,
    ):
        check_calendar.return_value = True
        stock_values.return_value = [
            {"symbol": "AAA", "exchange": "hose"},
            {"symbol": "ACB", "exchange": "hose"},
            {"symbol": "ACB", "exchange": "hose"},
            {"symbol": "TCB", "exchange": "hose"},
        ]
        etf_values.return_value = [
            {"symbol": "E1VFVND", "exchange": "hose"},
            {"symbol": "FUEVFVND", "exchange": "hose"},
        ]

        blob = self.bucket.blob(
            "marketdb/stock_price_intraday/2023/12/27/stock_price_ohlc.json"
        )
        file_path = self.__get_file_path(
            "files/stock_new_initializer/2023_12_27_stock_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        job = StockNewInitializer()
        success = job.pipeline(input_date="2023/12/27")
        self.assertTrue(success)

        stock_values.assert_called()
        etf_values.assert_called()

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_job_pipeline_no_data(self, check_calendar):
        check_calendar.return_value = True

        job = StockNewInitializer()
        success = job.pipeline(input_date="2100/04/15")
        self.assertFalse(success)
