import json
import pandas as pd
import unittest
import os

from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
from unittest.mock import patch

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stock_analytics.stock_price_analytics_intraday_job import (
    StockPriceAnalyticsIntradayJob,
)


class StockPriceAnalyticsIntradayJobTest(GcsTestCase, unittest.TestCase):
    file_path: str = "marketdb/jobs/pythontests/stock_analytics"
    bucket_name: str = "gcs-test-bucket"

    def __init__(self, *args, **kwargs):
        super(StockPriceAnalyticsIntradayJobTest, self).__init__(*args, **kwargs)

        os.environ["BUCKET_NAME"] = self.bucket_name

    def setUp(self):
        super().setUp(self.bucket_name)

    def get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    def test_compute_analytics(self):
        stock_analytics = [
            {
                "id": 1552,
                "created": "2023-03-16T11:10:06.843087+00:00",
                "modified": "2024-01-16T12:27:50.597311+00:00",
                "symbol": "ADG",
                "datetime": "2024-01-17T01:32:13.092+00:00",
                "reference": 21000.00,
                "price_1d": 20000.00,
                "volume_1d": 0.00,
                "fb_volume_1d": None,
                "fs_volume_1d": None,
                "change_percentage_1d": 156.81,
                "price_1w": 21100.00,
                "price_1m": 23400.00,
                "price_3m": 25300.00,
                "price_6m": 34000.00,
                "price_1y": 25050.00,
                "price_3y": None,
                "price_5y": None,
                "price_ytd": 21500.00,
                "price_inception_date": None,
                "change_percentage_1w": 148.58,
                "change_percentage_1m": 132.11,
                "change_percentage_3m": 114.68,
                "change_percentage_6m": 62.13,
                "change_percentage_1y": 103.05,
                "change_percentage_3y": None,
                "change_percentage_5y": None,
                "change_percentage_ytd": 152.63,
                "change_percentage_inception_date": None,
                "volume_1w": 6800.00,
                "volume_1m": 5200.00,
                "volume_3m": 500.00,
                "volume_6m": 9200.00,
                "volume_1y": 1600.00,
                "volume_3y": None,
                "volume_5y": None,
                "date": "2024-01-17",
            },
            {
                "id": 1564,
                "created": "2023-03-16T11:10:19.061012+00:00",
                "modified": "2024-01-16T14:40:21.41219+00:00",
                "symbol": "AIC",
                "datetime": "2024-01-17T01:32:18.139+00:00",
                "reference": 13800.00,
                "price_1d": 13500.00,
                "volume_1d": 0.00,
                "fb_volume_1d": None,
                "fs_volume_1d": None,
                "change_percentage_1d": 0.00,
                "price_1w": 14700.00,
                "price_1m": 14400.00,
                "price_3m": 9100.00,
                "price_6m": 10500.00,
                "price_1y": 9600.00,
                "price_3y": 28700.00,
                "price_5y": None,
                "price_ytd": 14600.00,
                "price_inception_date": None,
                "change_percentage_1w": -2.68,
                "change_percentage_1m": 0.69,
                "change_percentage_3m": 55.91,
                "change_percentage_6m": 39.42,
                "change_percentage_1y": 52.63,
                "change_percentage_3y": -49.48,
                "change_percentage_5y": None,
                "change_percentage_ytd": -0.68,
                "change_percentage_inception_date": None,
                "volume_1w": 8200.00,
                "volume_1m": 4520.00,
                "volume_3m": 200.00,
                "volume_6m": 2839.00,
                "volume_1y": 600.00,
                "volume_3y": 5900.00,
                "volume_5y": None,
                "date": "2024-01-17",
            },
        ]

        analytics_job = StockPriceAnalyticsIntradayJob()
        analytics_job.data_frame = pd.DataFrame(stock_analytics)

        computed_items = analytics_job.data_frame.apply(
            lambda row: analytics_job.compute_analytics(row["reference"], row), axis=1
        )

        self.assertFalse(computed_items.empty)
        self.assertEqual(computed_items.shape, (2, 37))

        self.assertEqual(computed_items.loc[0]["change_percentage_1d"], 5.0)

    @patch("requests.post")
    def test_do_indexing_sucess(self, mock_request):
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

        stock_analytics_job = StockPriceAnalyticsIntradayJob()
        success, result = stock_analytics_job.do_indexing(items=payload["items"])

        self.assertEqual(success, True)
        self.assertIsNotNone(result)

        mock_request.assert_called_with(
            url="http://marketdb-api.marketdb:8088/marketdb-internal/v1/indexer/bulk",
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

    @patch(
        "pipelines.stock_analytics.stock_price_analytics_intraday_job.StockPriceAnalyticsIntradayJob.do_indexing"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_pipeline_success(
        self,
        mock_check_calendar,
        mock_indexing_analytics,
    ):
        mock_check_calendar.return_value = True
        mock_indexing_analytics.return_value = True, {"status": "success", "total": 2}

        input_date = "2024/01/17"

        # get the stock prices analytics on input date
        blob = self.bucket.blob(
            f"marketdb/stock_price_analytics/2024/01/17/stock_price_analytics.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_analytics/2024_01_17_stock_price_analytics.json"
        )
        blob.upload_from_filename(file_path)

        # get the intraday OHLC stock prices on input date
        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/2024/01/17/stock_price_ohlc.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_analytics/2024_01_17_stock_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # run analytics job
        analytics_job = StockPriceAnalyticsIntradayJob()
        analytics_job.pipeline(input_date=input_date)

        self.assertFalse(analytics_job.data_frame.empty)
        self.assertEqual(analytics_job.data_frame.shape, (3, 34))


if __name__ == "__main__":
    unittest.main()
