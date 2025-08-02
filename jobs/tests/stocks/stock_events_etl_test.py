import unittest
import logging
from unittest.mock import patch

from common.mdb.client import (
    MarketdbClient,
)

import numpy as np

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stocks.stock_events_etl import StockEventETL


class StockCorporateActionTest(GcsTestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/stocks"

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch.object(MarketdbClient, "update_or_create")
    def test_stock_corporate_action_job_success(self, mock_update_or_create):
        mock_update_or_create.return_value = True, {}

        blob = self.bucket.blob(
            "crawler/stock/corporate-events/ssi-iboard/2023/07/22/LPB_corporateEvents.json"
        )
        file_path = self.__get_file_path(
            "files/corporate_events/2023_07_22_LPB_corporateEvents.json"
        )
        blob.upload_from_filename(file_path)

        job = StockEventETL()
        indexed = job.pipeline(input_date="2023/07/22")

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(indexed, 2)

    @patch.object(MarketdbClient, "update_or_create")
    def test_stock_corporate_action_job_failed(self, mock_update_or_create):
        mock_update_or_create.return_value = False, {}

        blob = self.bucket.blob(
            "crawler/stock/corporate-events/ssi-iboard/2023/07/22/LPB_corporateEvents.json"
        )
        file_path = self.__get_file_path(
            "files/corporate_events/2023_07_22_LPB_corporateEvents.json"
        )
        blob.upload_from_filename(file_path)

        job = StockEventETL()
        indexed = job.pipeline(input_date="2023/07/22")

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(indexed, 0)
