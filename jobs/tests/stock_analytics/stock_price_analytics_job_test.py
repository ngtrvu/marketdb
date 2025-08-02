import json
import numpy as np
import pandas as pd
import unittest
import os

from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
from common.tinydwh.datetime_util import VN_TIMEZONE, str_to_datetime
from unittest.mock import patch, ANY

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stock_analytics.stock_price_analytics_job import (
    StockPriceAnalyticsJob,
)


class StockPriceAnalyticsJobTest(GcsTestCase, unittest.TestCase):
    file_path: str = "marketdb/jobs/pythontests/stock_analytics"
    bucket_name: str = "gcs-test-bucket"

    def __init__(self, *args, **kwargs):
        super(StockPriceAnalyticsJobTest, self).__init__(*args, **kwargs)

        os.environ["BUCKET_NAME"] = self.bucket_name

    def setUp(self):
        super().setUp(self.bucket_name)

    def get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    def test_compute(self):
        stock_price_ohlc_bulk = [
            {
                "symbol": "CMG",
                "type": "STOCK",
                "exchange": "HOSE",
                "timestamp": 1701677522000,
                "date": "2023-12-03",
                "reference": np.nan,
                "open": 48750,
                "high": 48800,
                "low": 47900,
                "close": 48400,
                "ceiling": 52200,
                "floor": 45400,
                "price": 48400,
                "volume": 185900.0,
                "trading_value": 9036775000.0,
            },
            {
                "symbol": "CMG",
                "type": "STOCK",
                "exchange": "HOSE",
                "timestamp": 1701418322000,
                "date": "2023-12-01",
                "reference": np.nan,
                "open": 48900,
                "high": 48900,
                "low": 48000,
                "close": 48800,
                "ceiling": 52300,
                "floor": 45500,
                "price": 48800,
                "volume": 78300.0,
                "trading_value": 3807340000.0,
            },
        ]

        intraday_ohlc = [
            {
                "symbol": "CMG",
                "type": "STOCK",
                "exchange": "HOSE",
                "timestamp": 1701677522000,
                "date": "2023-12-04",
                "reference": np.nan,
                "open": 49750,
                "high": 49800,
                "low": 48900,
                "close": 49400,
                "ceiling": 52200,
                "floor": 45400,
                "price": 49400,
                "volume": 185900.0,
                "trading_value": 9036775000.0,
            },
        ]

        analytics_job = StockPriceAnalyticsJob()
        analytics_job.data_frame = pd.DataFrame(stock_price_ohlc_bulk)
        analytics_job.intraday_df = pd.DataFrame(intraday_ohlc)

        self.assertEqual(len(analytics_job.analytics_rows), 0)
        self.assertEqual(len(analytics_job.chart_rows), 0)

        symbol = "CMG"
        current_date = str_to_datetime(
            "2023/12/04", date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        result = analytics_job.compute(symbol, current_date)

        self.assertTrue(result)

        self.assertEqual(len(analytics_job.analytics_rows), 1)
        self.assertEqual(len(analytics_job.chart_rows), 1)

        self.assertEqual(len(analytics_job.analytics_rows), 1)
        self.assertEqual(analytics_job.analytics_rows[0]["reference"], None)
        self.assertEqual(analytics_job.analytics_rows[0]["price_1y"], None)
        self.assertEqual(analytics_job.analytics_rows[0]["volume_1y"], None)

    @patch("requests.post")
    def test_indexing_analytics_sucess(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"status": "success"}

        payload = {
            "model_name": "StockPriceAnalytics",
            "key_fields": ["symbol"],
            "items": [
                {"symbol": "XYZ", "datetime": "2024-01-08 09:51:27.438178+00"},
                {"symbol": "ACB", "datetime": "2024-01-08 09:52:27.438178+00"},
                {"symbol": "VCB", "datetime": "2023-07-03 09:53:27.438178+00"},
            ],
        }

        stock_analytics_job = StockPriceAnalyticsJob()
        success, result = stock_analytics_job.indexing_analytics(items=payload["items"])

        self.assertEqual(success, True)
        self.assertIsNotNone(result)

        mock_request.assert_called_with(
            url="http://marketdb-api.marketdb:8088/marketdb-internal/v1/indexer/bulk",
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

    @patch("requests.post")
    def test_indexing_charts_success(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"status": "success"}

        payload = {
            "model_name": "StockPriceChart",
            "key_fields": ["symbol"],
            "items": [
                {"symbol": "XYZ", "datetime": "2024-01-08 09:51:27.438178+00"},
                {"symbol": "ACB", "datetime": "2024-01-08 09:52:27.438178+00"},
                {"symbol": "VCB", "datetime": "2024-01-08 09:53:27.438178+00"},
            ],
        }

        stock_analytics_job = StockPriceAnalyticsJob()
        success, result = stock_analytics_job.indexing_charts(items=payload["items"])

        self.assertEqual(success, True)
        self.assertIsNotNone(result)

        mock_request.assert_called_with(
            url="http://marketdb-api.marketdb:8088/marketdb-internal/v1/indexer/bulk",
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

    @patch(
        "common.mdb.client.MarketdbClient.get_etf_symbols"
    )
    @patch(
        "common.mdb.client.MarketdbClient.get_stock_symbols"
    )
    @patch(
        "pipelines.stock_analytics.stock_price_analytics_job.StockPriceAnalyticsJob.indexing_analytics"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_pipeline_success(
        self,
        mock_check_calendar,
        mock_indexing_analytics,
        mock_get_stock_symbols,
        mock_get_etf_symbols,
    ):
        mock_check_calendar.return_value = True
        mock_indexing_analytics.return_value = True, {"status": "success", "total": 2}
        mock_get_stock_symbols.return_value = ["CMG", "MAC"]
        mock_get_etf_symbols.return_value = []

        input_date = "2023/12/05"

        # get the bulk OHLC stock prices on previous trading date
        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/2023/12/04/stock_price_bulk.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc/2023_12_04_stock_price_bulk.json"
        )
        blob.upload_from_filename(file_path)

        # get the intraday OHLC stock prices on input date
        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/{input_date}/stock_price_ohlc.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_intraday/2023_12_05_stock_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # import pdb; pdb.set_trace();

        # run analytics job
        analytics_job = StockPriceAnalyticsJob()
        analytics_job.pipeline(input_date=input_date, data_type="analytics")

        self.assertEqual(analytics_job.data_frame.empty, False)
        self.assertEqual(analytics_job.intraday_df.empty, False)
        self.assertEqual(len(analytics_job.analytics_rows), 2)

        expected_items = [
            {
                "symbol": "CMG",
                "reference": 48800,
                "date": date(2023, 12, 5),
                "datetime": ANY,
                "price_1d": 48400.0,
                "price_1w": 48700.0,
                "price_1m": None,
                "price_3m": None,
                "price_6m": None,
                "price_1y": None,
                "price_3y": None,
                "price_5y": None,
                "price_ytd": None,
                "volume_1d": 185900.0,
                "volume_1w": 80000.0,
                "volume_1m": None,
                "volume_3m": None,
                "volume_6m": None,
                "volume_1y": None,
                "volume_3y": None,
                "volume_5y": None,
            },
            {
                "symbol": "MAC",
                "reference": 10200,
                "date": date(2023, 12, 5),
                "datetime": ANY,
                "price_1d": 10300.0,
                "price_1w": 9600.0,
                "price_1m": None,
                "price_3m": None,
                "price_6m": None,
                "price_1y": None,
                "price_3y": None,
                "price_5y": None,
                "price_ytd": None,
                "volume_1d": 75200.0,
                "volume_1w": 4800.0,
                "volume_1m": None,
                "volume_3m": None,
                "volume_6m": None,
                "volume_1y": None,
                "volume_3y": None,
                "volume_5y": None,
            },
        ]

        mock_indexing_analytics.assert_called_with(
            items=sorted(expected_items, key=lambda x: x["symbol"])
        )


if __name__ == "__main__":
    unittest.main()
