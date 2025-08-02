import unittest
from unittest.mock import patch

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stocks.stock_corporate_action import (
    StockCorporateAction,
)


class StockCorporateActionTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/stocks"

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "pipelines.stocks.stock_corporate_action.StockCorporateAction"
        ".get_next_trading_date_str"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_corporate_action_success(
        self, check_calendar, get_next_trading_date_str
    ):
        check_calendar.return_value = True
        get_next_trading_date_str.return_value = "2023/12/04"

        input_date = "2023/12/03"

        blob = self.bucket.blob(
            f"marketdb/stock_event_1y/{input_date}/by_public_date.json"
        )
        file_path = self.__get_file_path(
            "files/stock_corporate_action/marketdb_stock_event_1y_2023_12_03_by_public_date.json"
        )
        blob.upload_from_filename(file_path)

        blob = self.bucket.blob(
            f"marketdb/corporate_action/2023/12/04/corporate_action.json"
        )
        file_path = self.__get_file_path(
            "files/stock_corporate_action/marketdb_corporate_action_2023_12_04_corporate_action.json"
        )
        blob.upload_from_filename(file_path)

        job = StockCorporateAction()
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(job.data_frame.shape, (4, 10))

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_job_pipeline_no_data(self, check_calendar):
        check_calendar.return_value = True
        job = StockCorporateAction()
        job.pipeline(input_date="2023/12/03")

        self.assertTrue(job.data_frame.empty)
