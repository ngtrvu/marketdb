from datetime import datetime

from django.urls import reverse
from pytz import timezone
from rest_framework import status

from common.utils.datetime_util import VN_TIMEZONE
from core.models.stocks.stock_price_analytics import StockPriceAnalytics
from core.models import StockPriceRealtime
from core.models.stocks.stock_event import StockEvent
from tests.factories.stock_price_analytics import (
    StockPriceAnalyticsFactory,
)
from tests.factories.stock_event import StockEventFactory
from tests.testutils.apitest import AdminAPITest
from tests.factories.industry import IndustryFactory


class UpdateBulkTestCase(AdminAPITest):
    def setUp(self):
        super(UpdateBulkTestCase, self).setUp()

    def test_update_bulk_success(self):
        now = datetime.now(tz=timezone(VN_TIMEZONE))
        StockPriceAnalyticsFactory(symbol="ACB", datetime=now)
        StockPriceAnalyticsFactory(symbol="HPG", datetime=now, date="2000-01-01")

        url = reverse("api_internal:indexer-bulk-update")
        data = {
            "model_name": "StockPriceAnalytics",
            "values": {
                "datetime": "2023-07-03 09:50:27.438178+00",
            },
            "conditions": {"symbol": "ACB"},
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = StockPriceAnalytics.objects.get(symbol="ACB")
        self.assertEqual(item.datetime.year, 2023)
        self.assertEqual(item.datetime.month, 7)
        self.assertEqual(item.datetime.day, 3)

        url = reverse("api_internal:indexer-bulk-update")
        data = {
            "model_name": "StockPriceAnalytics",
            "values": {
                "datetime": "2022-07-03 09:50:27.438178+00",
            },
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = StockPriceAnalytics.objects.get(symbol="ACB")
        self.assertEqual(item.datetime.year, 2022)

        item = StockPriceAnalytics.objects.get(symbol="HPG")
        self.assertEqual(item.datetime.year, 2022)

    def test_update_invalid(self):
        url = reverse("api_internal:indexer-bulk-update")
        data = {
            "model_name": "StockPriceAnalytics",
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse("api_internal:indexer-bulk-update")
        data = {
            "model_name": "dummy",
            "values": {"symbol": "ACB", "datetime": "2023-07-03 09:50:27.438178+00"},
            "conditions": {"symbol": "ACB"},
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
