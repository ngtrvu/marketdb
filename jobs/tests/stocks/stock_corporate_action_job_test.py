import unittest
from unittest.mock import patch

import numpy as np

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stocks.stock_corporate_action_job import (
    StockCorporateActionJob,
)


class StockCorporateActionJobTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/stocks"

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "pipelines.stocks.stock_corporate_action_job.StockCorporateActionJob"
        ".get_previous_trading_date_str"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_corporate_action_job_success(
        self, check_calendar, get_previous_trading_date_str
    ):
        check_calendar.return_value = True
        get_previous_trading_date_str.return_value = "2023/04/14"

        blob = self.bucket.blob("marketdb/stock_event_log/stock_event_bulk.json")
        file_path = self.__get_file_path(
            "files/stock_corporate_action/marketdb_stock_event_stock_event_bulk.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            "marketdb/stock_price_intraday/2023/04/14/stock_price_ohlc.json"
        )
        file_path = self.__get_file_path(
            "files/stock_corporate_action/2023_04_14_ssi_iboard_stock_dailyPrices.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            "marketdb/stock_price_intraday/2023/04/17/stock_price_ohlc.json"
        )
        file_path = self.__get_file_path(
            "files/stock_corporate_action/2023_04_17_ssi_iboard_stock_dailyPrices.json"
        )
        blob.upload_from_filename(file_path)

        job = StockCorporateActionJob()
        job.pipeline(input_date="2023/04/17")

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(len(job.data_frame.index), 5)

        sbs_row = job.data_frame[job.data_frame["symbol"] == "CBS"].to_dict(
            orient="records"
        )[0]
        self.assertEqual(sbs_row["dividend_type"], "STOCK")
        self.assertIsNotNone(sbs_row["date"])
        self.assertGreater(sbs_row["stock"], 0)
        self.assertTrue(np.isnan(sbs_row["cash"]))

        sbs_row = job.data_frame[job.data_frame["symbol"] == "DHD"].to_dict(
            orient="records"
        )[0]
        self.assertEqual(sbs_row["dividend_type"], "CASH")
        self.assertIsNotNone(sbs_row["date"])
        self.assertGreater(sbs_row["cash"], 0)
        self.assertTrue(np.isnan(sbs_row["stock"]))

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_job_pipeline_no_data(self, check_calendar):
        check_calendar.return_value = True
        job = StockCorporateActionJob()
        job.pipeline(input_date="2024/04/19")

        self.assertTrue(job.data_frame.empty)
