from datetime import datetime

from django.urls import reverse
from pytz import timezone
from rest_framework import status

from common.utils.datetime_util import VN_TIMEZONE
from core.models.market_index.market_index import MarketIndex
from core.models.market_index.market_index import MarketIndexStock
from core.models.stocks.stock import Stock
from core.models.stocks.stock_price_analytics import StockPriceAnalytics
from core.models import StockPriceRealtime
from core.models.stocks.stock_event import StockEvent
from tests.factories.stock_price_analytics import (
    StockPriceAnalyticsFactory,
)
from tests.factories.stock_event import StockEventFactory
from tests.testutils.apitest import AdminAPITest
from tests.factories.industry import IndustryFactory
from tests.factories.market_index import MarketIndexFactory
from tests.factories.stock import StockFactory


class IndexerBulkTestCase(AdminAPITest):
    def setUp(self):
        MarketIndexFactory(symbol="VN30")
        StockFactory(symbol="ACB")
        StockFactory(symbol="TCB")
        StockFactory(symbol="VCB")

    def tearDown(self):
        MarketIndexStock.objects.all().delete()
        MarketIndex.objects.all().delete()
        Stock.objects.all().delete()

    def test_create_or_update_success(self):
        now = datetime.now(tz=timezone(VN_TIMEZONE))
        StockPriceAnalyticsFactory(symbol="ACB", datetime=now)
        StockPriceAnalyticsFactory(symbol="HPG", datetime=now, date="2000-01-01")

        url = reverse("api_internal:bulk-data-indexer")
        data = {
            "model_name": "StockPriceAnalytics",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "ACB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "solomon": "123",
                },
                {
                    "symbol": "VCB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "solomon": "123",
                },
                {
                    "symbol": "HPG",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "solomon": "123",
                },
            ],
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item = StockPriceAnalytics.objects.get(symbol="ACB")
        self.assertEqual(item.datetime.year, 2023)
        self.assertEqual(item.datetime.month, 7)
        self.assertEqual(item.datetime.day, 3)

        item = StockPriceAnalytics.objects.get(symbol="VCB")
        self.assertEqual(item.datetime.year, 2023)
        self.assertEqual(item.datetime.month, 7)
        self.assertEqual(item.datetime.day, 3)

        item = StockPriceAnalytics.objects.get(symbol="HPG")
        self.assertEqual(item.datetime.year, 2023)
        self.assertEqual(item.datetime.month, 7)
        self.assertEqual(item.datetime.day, 3)

        # test multiple field keys
        StockEventFactory(symbol="ACB", public_date="2023-07-03", name="something")
        data = {
            "model_name": "StockEvent",
            "key_fields": ["symbol", "public_date", "name"],
            "items": [
                {
                    "symbol": "ACB",
                    "public_date": "2023-07-03",
                    "name": "something",
                    "title": "my title",
                },
                {
                    "symbol": "ACB",
                    "public_date": "2023-08-03",
                    "name": "something",
                    "title": "my title",
                },
                {
                    "symbol": "ACB",
                    "public_date": "2023-09-03",
                    "name": "something",
                    "title": "my title",
                },
                {
                    "symbol": "VCB",
                    "public_date": "2023-07-03",
                    "name": "something",
                    "title": "blahblah",
                },
                {
                    "symbol": "VCB",
                    "public_date": "2023-07-02",
                    "name": "something",
                    "title": "blahblah",
                },
                {
                    "symbol": "HPG",
                    "public_date": "2023-07-04",
                    "name": "something",
                    "title": "123",
                },
            ],
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item = StockEvent.objects.get(symbol="HPG")
        self.assertEqual(item.public_date.year, 2023)
        self.assertEqual(item.public_date.month, 7)
        self.assertEqual(item.public_date.day, 4)

        data = {
            "model_name": "StockPriceRealtime",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "FIR",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "volume": 754900,
                    "total_trading_value": 10467000000,
                    "reference": 13600,
                    "open": 14200,
                    "low": 13600,
                    "high": 14200,
                    "close": 13600,
                    "price": 13600,
                },
                {
                    "symbol": "ACB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "volume": 754900,
                    "total_trading_value": 10467000000,
                    "reference": 13600,
                    "open": 14200,
                    "low": 13600,
                    "high": 14200,
                    "close": 13600,
                    "price": 13600,
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["total"], 2)

        item = StockPriceRealtime.objects.get(symbol="FIR")
        self.assertEqual(item.symbol, "FIR")
        self.assertEqual(item.volume, 754900)
        self.assertEqual(item.total_trading_value, 10467000000)

        item = StockPriceRealtime.objects.get(symbol="ACB")

        data = {
            "model_name": "StockPriceRealtime",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "FIR",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "volume": 754900,
                    "total_trading_value": 10467000000,
                    "price": 13600,
                },
                {
                    "symbol": "ACB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "volume": 754900,
                    "total_trading_value": 10467000000,
                    "price": 13600,
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        industry1 = IndustryFactory(id=10001, name="Industry 1", icb_code=1000)

        data = {
            "model_name": "IndustryAnalytics",
            "key_fields": ["industry_id"],
            "items": [
                {
                    "industry_id": 10001,
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "market_cap": 100,
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "model_name": "core.IndustryAnalytics",
            "key_fields": ["industry_id"],
            "items": [
                {
                    "industry_id": 10001,
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "market_cap": 100,
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "model_name": "core.Stock",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "ACB",
                    "exchange": "HOSE",
                    "type": "stock",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "model_name": "core.Stock",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "FPT",
                    "exchange": "HOSE",
                    "type": "stock",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                },
                {
                    "symbol": "FPT",
                    "exchange": "HOSE",
                    "type": "stock",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_or_update_only_key_fields_success(self):
        url = reverse("api_internal:bulk-data-indexer")
        data = {
            "model_name": "MarketIndexStock",
            "key_fields": ["stock_id", "market_index_id"],
            "items": [
                {
                    "stock_id": "ACB",
                    "market_index_id": "VN30",
                },
                {
                    "stock_id": "TCB",
                    "market_index_id": "VN30",
                },
                {
                    "stock_id": "VCB",
                    "market_index_id": "VN30",
                },
            ],
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_or_update_invalid(self):
        url = reverse("api_internal:bulk-data-indexer")
        data = {
            "model_name": "StockPriceAnalytics",
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_or_update_failed(self):
        url = reverse("api_internal:bulk-data-indexer")
        data = {
            "model_name": "dummy",
            "key_fields": ["symbol"],
            "items": [
                {"symbol": "ACB", "datetime": "2023-07-03 09:50:27.438178+00"},
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "dummy",
            "key_fields": ["symbol"],
            "items": [
                {"symbol": "ACB"},
            ],
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "StockPriceAnalytics",
            "key_fields": ["symbol"],
            "items": [
                {"key_value": "ACB", "payload": {}},
                {"symbol": "ACB", "datetime": "2023-07-03 09:50:27.438178+00"},
                {"symbol": "VCB", "datetime": "2023-07-03 09:50:27.438178+00"},
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "StockPriceAnalytics",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "ACB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "price_1d": 10000000000000000000000000000000000000000000000000000,
                },
                {
                    "symbol": "VCB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "price_1d": 10000,
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "StockPriceAnalytics",
            "key_fields": ["symbol"],
            "items": [
                {
                    "symbol": "ACB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                    "price_1d": 10,
                },
                {
                    "symbol": "VCB",
                    "datetime": "2023-07-03 09:50:27.438178+00",
                },
            ],
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_or_update_db_failed(self):
        url = reverse("api_internal:bulk-data-indexer") 
        data = {
            "model_name": "MarketIndexStock",
            "key_fields": ["stock_id", "market_index_id"],
            "items": [
                {
                    "stock_id": "ACB",
                    "market_index_id": "VN30",
                },
                {
                    "stock_id": "XYZ",
                    "market_index_id": "ABC",
                },
            ],
        }

        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"success": True, "total": 2, 'warning': ''})
