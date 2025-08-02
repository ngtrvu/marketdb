import json
import os
import unittest
from unittest.mock import ANY, patch

from django.core.serializers.json import DjangoJSONEncoder
from google.cloud import storage

from common.tinydwh.storage.test_utils import GcsEmulator, GcsTestCase
from pipelines.industry.industry_analytics_daily_job import (
    IndustryAnalyticsDailyJob,
)


class IndustryTest(GcsTestCase, unittest.TestCase):
    file_path: str = "marketdb/jobs/pythontests/industry"
    bucket_name: str = "gcs-test-bucket"

    def __init__(self, *args, **kwargs):
        super(IndustryTest, self).__init__(*args, **kwargs)

        os.environ["BUCKET_NAME"] = self.bucket_name

    def setUp(self):
        super().setUp(self.bucket_name)

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar",
    )
    @patch(
        "common.mdb.client.MarketdbClient.index_to_db_bulk"
    )
    def test_job_pipeline_success(self, mock_index_to_db_bulk, check_calendar):
        check_calendar.return_value = True
        mock_index_to_db_bulk.return_value = True, {"status": "success"}

        blob = self.bucket.blob("marketdb/industry/2023/04/05/industry.json")
        file_path = self.__get_file_path(
            "files/marketdb_industry_2023_04_05_industry.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob("marketdb/stock/2023/04/05/stock.json")
        file_path = self.__get_file_path("files/marketdb_stock_2023_04_05_stock.json")
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            "marketdb/stock_price_analytics/2023/04/05/stock_price_analytics.json"
        )
        file_path = self.__get_file_path(
            "files/marketdb_stock_price_analytics_2023_04_05_stock_price_analytics.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            "marketdb/stock_price_ohlc_daily/2023/04/04/stock_price_ohlc_daily.json"
        )
        file_path = self.__get_file_path(
            "files/marketdb_stock_price_ohlc_daily_2023_04_04_stock_price_ohlc_daily.json"
        )
        blob.upload_from_filename(file_path)

        job = IndustryAnalyticsDailyJob()
        job.pipeline(input_date="2023/04/05")

        self.assertEqual(check_calendar.call_count, 2)

        dfs = job.get_result_dataframe()
        self.assertEqual(len(dfs), 4)

        industry_df = dfs[0]
        expected_columns = [
            "change_percentage_1d",
            "change_percentage_1m",
            "change_percentage_1w",
            "change_percentage_1y",
            "change_percentage_3m",
            "change_percentage_3y",
            "change_percentage_5y",
            "change_percentage_6m",
            "change_percentage_ytd",
            "icb_code",
            "industry_id",
            "market_cap",
            "market_cap_1d",
            "market_cap_1m",
            "market_cap_1w",
            "market_cap_1y",
            "market_cap_3m",
            "market_cap_3y",
            "market_cap_5y",
            "market_cap_6m",
            "market_cap_ytd",
            "datetime",
        ]
        self.assertEqual(
            sorted(expected_columns),
            sorted(list(dfs[0].columns)),
        )
        self.assertEqual(
            sorted(expected_columns),
            sorted(list(dfs[1].columns)),
        )
        self.assertEqual(
            sorted(expected_columns),
            sorted(list(dfs[2].columns)),
        )
        self.assertEqual(
            sorted(expected_columns),
            sorted(list(dfs[3].columns)),
        )

        self.assertEqual(dfs[0].iloc[0]["industry_id"], 10001)

        # verify banking industry : icb_code = 8000
        banking_market_cap_today = (
            25150.00 * 3377435094 + 92000.00 * 4732516571 + 29500.00 * 35172385140
        )
        banking_market_cap_1d = (
            25000.00 * 3377435094 + 91400.00 * 4732516571 + 28350.00 * 35172385140
        )
        banking_market_cap_1w = (
            24400.00 * 3377435094 + 92300.00 * 4732516571 + 28000.00 * 35172385140
        )
        banking_market_cap_1m = (
            24500.00 * 3377435094 + 90900.00 * 4732516571 + 26800.00 * 35172385140
        )
        banking_market_cap_3m = (
            22850.00 * 3377435094 + 84000.00 * 4732516571 + 27650.00 * 35172385140
        )
        banking_market_cap_6m = (
            20800.00 * 3377435094 + 71500.00 * 4732516571 + 30500.00 * 35172385140
        )
        banking_market_cap_1y = (
            26400.00 * 3377435094 + 83000.00 * 4732516571 + 49050.00 * 35172385140
        )

        expected_banking_1d = (
            (banking_market_cap_today - banking_market_cap_1d)
            * 100
            / banking_market_cap_1d
        )
        expected_banking_1w = (
            (banking_market_cap_today - banking_market_cap_1w)
            * 100
            / banking_market_cap_1w
        )
        expected_banking_1m = (
            (banking_market_cap_today - banking_market_cap_1m)
            * 100
            / banking_market_cap_1m
        )
        expected_banking_3m = (
            (banking_market_cap_today - banking_market_cap_3m)
            * 100
            / banking_market_cap_3m
        )
        expected_banking_6m = (
            (banking_market_cap_today - banking_market_cap_6m)
            * 100
            / banking_market_cap_6m
        )
        expected_banking_1y = (
            (banking_market_cap_today - banking_market_cap_1y)
            * 100
            / banking_market_cap_1y
        )

        computed_banking = industry_df[industry_df["icb_code"] == 8000].iloc[0]
        self.assertEqual(expected_banking_1d, computed_banking["change_percentage_1d"])
        self.assertEqual(expected_banking_1w, computed_banking["change_percentage_1w"])
        self.assertEqual(expected_banking_1m, computed_banking["change_percentage_1m"])
        self.assertEqual(expected_banking_3m, computed_banking["change_percentage_3m"])
        self.assertEqual(expected_banking_6m, computed_banking["change_percentage_6m"])
        self.assertEqual(expected_banking_1y, computed_banking["change_percentage_1y"])

        # verify: icb_code = 1000 ~ HPG only in sample data
        hpg_market_cap_today = 21100.00 * 5814785700
        hpg_market_cap_1d = 20800.00 * 5814785700
        expected_hpg_change_percentage_1d = (
            (hpg_market_cap_today - hpg_market_cap_1d) * 100 / hpg_market_cap_1d
        )
        computed_hpg_change_percentage_1d = industry_df[
            industry_df["icb_code"] == 1000
        ].iloc[0]["change_percentage_1d"]
        self.assertEqual(
            expected_hpg_change_percentage_1d, computed_hpg_change_percentage_1d
        )

        # verify: icb_code = 0500 ~ PLX, OIL only in sample data
        computed_petro_change_percentage_1d = industry_df[
            industry_df["icb_code"] == 1
        ].iloc[0]["change_percentage_1d"]
        self.assertTrue(computed_petro_change_percentage_1d > 0)

        mock_index_to_db_bulk.assert_called_with(
            model_name="IndustryAnalytics", key_fields=["industry_id"], payload=ANY
        )

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    @patch(
        "common.mdb.client.MarketdbClient.index_to_db_bulk"
    )
    def test_job_pipeline_no_data(self, mock_index_to_db_bulk, check_calendar):
        check_calendar.return_value = True
        mock_index_to_db_bulk.return_value = True, {"status": "success"}

        job = IndustryAnalyticsDailyJob()
        job.pipeline(input_date="2023/04/06")
        self.assertTrue(job.data_frame.empty)

    @patch("requests.post")
    def test_indexing_df_sucess(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"status": "success"}

        payload = {
            "model_name": "IndustryAnalytics",
            "key_fields": ["industry_id"],
            "items": [
                {"industry_id": 111, "datetime": "2024-01-08 09:51:27.438178+00"},
                {"industry_id": 222, "datetime": "2024-01-08 09:52:27.438178+00"},
                {"industry_id": 333, "datetime": "2023-07-03 09:53:27.438178+00"},
            ],
        }

        stock_analytics_job = IndustryAnalyticsDailyJob()
        success, result = stock_analytics_job.indexing_df(items=payload["items"])

        self.assertEqual(success, True)
        self.assertIsNotNone(result)

        mock_request.assert_called_with(
            url="http://marketdb-api.marketdb:8088/marketdb-internal/v1/indexer/bulk",
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            headers={"Content-Type": "application/json"},
             timeout=10,
        )


if __name__ == "__main__":
    unittest.main()
