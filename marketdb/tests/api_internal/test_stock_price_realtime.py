from datetime import datetime
from unittest.mock import patch

from dateutil.tz import tzoffset
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.libs.intraday.intraday_manager import IntradayManager
from tests.factories.stock import StockFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory
from tests.testutils.apitest import APITest


class StockPriceRealtimeApiTestCase(APITest):
    def setUp(self):
        super(StockPriceRealtimeApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau")
        self.stock2 = StockFactory(symbol="VCB", name="Ngan hang vietcombank")

        stock_datetime = datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))
        self.stock_price_1 = StockPriceRealtimeFactory(
            symbol="ACB", price=21.0, reference=20.0, volume=1000, datetime=stock_datetime
        )
        self.stock_price_2 = StockPriceRealtimeFactory(
            symbol="VCB", price=80.0, reference=79.0, volume=1000, datetime=stock_datetime
        )

        self.client = APIClient()

    @patch.object(IntradayManager, "get_prices")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_redis_return_empty(self, init, get_prices):
        init.return_value = None
        time = datetime(2022, 12, 14, 14, 37, 40, tzinfo=tzoffset(None, 25200)).timestamp()
        get_prices.return_value = {}

        url = reverse("api_internal:stock-price-realtime-list")
        url = url + "?symbol__in=ACB,VCB"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["symbol"], "VCB")
        self.assertEqual(response.data[0]["price"], 80.0)
        self.assertEqual(response.data[0]["reference"], 79.0)
        self.assertEqual(response.data[0]["volume"], 1000)

        self.assertEqual(response.data[1]["symbol"], "ACB")
        self.assertEqual(response.data[1]["price"], 21.0)
        self.assertEqual(response.data[1]["reference"], 20.0)
        self.assertEqual(response.data[1]["volume"], 1000)

    @patch.object(IntradayManager, "get_prices")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_db_success(self, init, get_prices):
        init.return_value = None
        time = datetime(2022, 12, 14, 14, 37, 40, tzinfo=tzoffset(None, 25200)).timestamp()
        get_prices.return_value = {
            "ACB": {
                "price": None,
                "timestamp": int(time),
            },
            "VCB": {
                "price": 0,
                "timestamp": int(time),
            },
        }

        url = reverse("api_internal:stock-price-realtime-list")
        url = url + "?symbol__in=ACB,VCB"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["symbol"], "VCB")
        self.assertEqual(response.data[0]["price"], 80.0)
        self.assertEqual(response.data[0]["reference"], 79.0)
        self.assertEqual(response.data[0]["volume"], 1000)

        self.assertEqual(response.data[1]["symbol"], "ACB")
        self.assertEqual(response.data[1]["price"], 21.0)
        self.assertEqual(response.data[1]["reference"], 20.0)
        self.assertEqual(response.data[1]["volume"], 1000)

    @patch.object(IntradayManager, "get_prices")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_acb_get_redis_vcb_fallback_get_db(self, init, get_prices):
        init.return_value = None
        time = datetime(2022, 12, 15, 14, 37, 40, tzinfo=tzoffset(None, 25200)).timestamp()
        get_prices.return_value = {
            "ACB": {
                "price": 21.5,
                "timestamp": float(time),
            },
            "VCB": {
                "price": None,
                "timestamp": float(time),
            },
        }

        url = reverse("api_internal:stock-price-realtime-list")
        url = url + "?symbol__in=ACB,VCB"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["symbol"], "VCB")
        self.assertEqual(response.data[0]["price"], 80.0)
        self.assertEqual(response.data[0]["reference"], 79.0)
        self.assertEqual(response.data[0]["volume"], 1000)

        self.assertEqual(response.data[1]["symbol"], "ACB")
        self.assertEqual(response.data[1]["price"], 21.5)
        self.assertEqual(response.data[1]["reference"], 20.0)
        self.assertEqual(response.data[1]["volume"], 1000)

    @patch.object(IntradayManager, "get_prices")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_acb_and_vcb_get_redis(self, init, get_prices):
        init.return_value = None
        time = datetime(2022, 12, 15, 14, 37, 40, tzinfo=tzoffset(None, 25200)).timestamp()
        get_prices.return_value = {
            "ACB": {
                "price": 21.5,
                "timestamp": int(time),
            },
            "VCB": {
                "price": 79.5,
                "timestamp": int(time),
            },
        }

        url = reverse("api_internal:stock-price-realtime-list")
        url = url + "?symbol__in=ACB,VCB"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["symbol"], "VCB")
        self.assertEqual(response.data[0]["price"], 79.5)
        self.assertEqual(response.data[0]["reference"], 79.0)
        self.assertEqual(response.data[0]["volume"], 1000)

        self.assertEqual(response.data[1]["symbol"], "ACB")
        self.assertEqual(response.data[1]["price"], 21.5)
        self.assertEqual(response.data[1]["reference"], 20.0)
        self.assertEqual(response.data[1]["volume"], 1000)
