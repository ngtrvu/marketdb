import logging

import unittest
from unittest.mock import patch


from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.market_index.market_index_intraday_job import (
    MarketIndexIntradayJob,
)


class MarketIndexIntradayTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/market_index"

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch("common.mdb.client.MarketdbClient.update_or_create")
    def test_market_index_intraday_job_success(self, update_or_create):
        update_or_create.return_value = True

        blob = self.bucket.blob(
            "marketdb/market_index_ohlc/2023/12/26/market_index_ohlc.json"
        )
        file_path = self.__get_file_path(
            "files/market_index_intraday/2023_12_26_market_index_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        job = MarketIndexIntradayJob()
        job.pipeline(input_date="2023/12/26")

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(len(job.data_frame.index), 4)

        row = job.items[0]
        self.assertEqual(row["symbol"], "VNINDEX")
        self.assertEqual(row["exchange"], "HOSE")
        self.assertEqual(row["open"], 1117.66)
        self.assertEqual(row["close"], 1122.25)
        self.assertEqual(row["volume"], 644741653)
        self.assertEqual(round(row["change_percentage_1d"], 4), 0.4107)
        self.assertEqual(row["total_trading_value"], 14738587000000)

        self.assertEqual(update_or_create.call_count, 4)

    def test_job_pipeline_no_data(self):
        job = MarketIndexIntradayJob()
        job.pipeline(input_date="2024/01/01")

        self.assertTrue(job.data_frame.empty)
