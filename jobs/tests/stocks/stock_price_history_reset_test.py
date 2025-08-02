import unittest
from unittest.mock import patch

import numpy as np

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stock_prices.stock_price_history_reset import (
    StockPriceHistoryReset,
)


class StockPriceHistoryResetTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/stocks"

    def get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_job_pipeline_no_data(self, check_calendar):
        check_calendar.return_value = True
        job = StockPriceHistoryReset()
        job.pipeline(input_date="2345/01/01")

        self.assertTrue(job.data_frame.empty)

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_bulk_reset_success(self, check_calendar):
        check_calendar.return_value = True
        input_date = "2023/05/09"

        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v2/{input_date}/trigger.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_bulk_transform_v2/marketdb_stock_price_ohlc_bulk_v2_2023_05_08_short.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            f"crawler/vndirect_stock_price_bulk/{input_date}/trigger.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_bulk_transform_v2/marketdb_stock_price_ohlc_bulk_2023_05_08_short.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/{input_date}/trigger.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_bulk_transform_v2/2023_05_09_ssi_iboard_stock_dailyPrices.json"
        )
        blob.upload_from_filename(file_path)

        # run job at the end of the day
        job = StockPriceHistoryReset()
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertTupleEqual(job.data_frame.shape, (86, 8))

        # Check the normalization of VIM's close prices on the day of no trading
        vim_prices = job.data_frame.query("symbol == 'VIM'").iloc[0]
        self.assertEqual(vim_prices["reference"], vim_prices["close"])
        nan_open_high_low = (
            np.isnan(vim_prices["open"])
            and np.isnan(vim_prices["high"])
            and np.isnan(vim_prices["low"])
        )
        self.assertTrue(nan_open_high_low)
