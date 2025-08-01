import unittest
from unittest.mock import patch
from datetime import datetime

from django.urls import reverse
from pytz import timezone
from rest_framework import status

from utils.dj_exporter import DjExporter
from common.utils.datetime_util import VN_TIMEZONE
from core.models.market.market_calendar import MarketStatusEnum
from tests.factories.market_calendar import MarketCalendarFactory
from tests.factories.industry import IndustryFactory
from tests.testutils.apitest import AdminAPITest


class TableExporterTestCase(AdminAPITest):
    def setUp(self):
        super(TableExporterTestCase, self).setUp()

    @patch.object(DjExporter, "export_table_to_gcs")
    def test_export_table_failed(self, mock_export_gcs):
        url = reverse("api_internal:table-exporter")
        data = {
            "table_name": "stock",
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_export_gcs.assert_not_called()

        data = {
            "table_name": "dummy",
            "dataset_name": "demo",
            "bucket_name": "bucket",
        }
        mock_export_gcs.return_value = False

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        today_in_string = datetime.now(timezone(VN_TIMEZONE)).strftime("%Y/%m/%d")
        mock_export_gcs.assert_called_with(
            table_name="dummy",
            dataset_name="demo",
            bucket_name="bucket",
            directory_name="dummy",
            input_date=today_in_string,
        )

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(DjExporter, "export_table_to_gcs")
    def test_export_table_success(self, mock_export_gcs):
        url = reverse("api_internal:table-exporter")
        data = {
            "table_name": "stock",
            "dataset_name": "demo",
            "bucket_name": "bucket",
            "directory_name": "new_dir",
            "input_date": "2024-09-09",
        }
        mock_export_gcs.return_value = True

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_export_gcs.assert_called_once()
        mock_export_gcs.assert_called_with(
            table_name="stock",
            dataset_name="demo",
            bucket_name="bucket",
            directory_name="new_dir",
            input_date="2024-09-09",
        )
