import unittest
from unittest.mock import patch

import pandas as pd

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stock_prices.stock_price_history_by_time import (
    StockPriceHistoryByTime,
)


class StockPriceHistoryByTimeTest(GcsTestCase):
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
        job = StockPriceHistoryByTime()
        job.pipeline(input_date="2345/01/01")

        self.assertTrue(job.data_frame.empty)

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_history_by_time_success(self, check_calendar):
        check_calendar.return_value = True
        input_date = "2023/05/09"

        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/{input_date}/trigger.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_bulk_transform_v2/marketdb_stock_price_ohlc_bulk_v2_2023_05_08_short.json"
        )
        blob.upload_from_filename(file_path)

        bulk_price_test_df = pd.read_json(file_path, lines=True)

        trading_dates = bulk_price_test_df["date"].drop_duplicates()
        trading_dates_str = trading_dates.dt.strftime("%Y/%m/%d")
        for date_str in trading_dates_str:
            blob = self.bucket.blob(
                f"marketdb/stock_price_ohlc_daily/{date_str}/trigger.json"
            )
            file_path = self.get_file_path(
                "files/stock_price_bulk_transform_v2/2023_05_09_ssi_iboard_stock_dailyPrices.json"
            )
            blob.upload_from_filename(file_path)

        trading_years_str = (
            bulk_price_test_df["date"].dt.strftime("%Y").drop_duplicates().tolist()
        )
        for year_str in trading_years_str:
            blob = self.bucket.blob(
                f"marketdb/stock_price_ohlc_yearly/{year_str}/trigger.json"
            )
            file_path = self.get_file_path(
                "files/stock_price_bulk_transform_v2/marketdb_stock_price_ohlc_bulk_v2_2023_05_08_short.json"
            )
            blob.upload_from_filename(file_path)

        symbols = bulk_price_test_df["symbol"].unique()
        for symbol in symbols:
            blob = self.bucket.blob(f"marketdb/stock_price_ohlc/{symbol}.json")
            file_path = self.get_file_path(
                "files/stock_price_bulk_transform_v2/2023_05_09_ssi_iboard_stock_dailyPrices.json"
            )
            blob.upload_from_filename(file_path)

        # run job at the end of trading date
        job = StockPriceHistoryByTime()
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)

        # # Check the VIM's close prices on the day of no trading
        # vim_prices = job.data_frame.query("symbol == 'VIM'").iloc[0]
        # self.assertEqual(vim_prices["close"], 0)
