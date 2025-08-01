from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime
from dateutil.tz import tzutc, tzoffset

from core.libs.intraday.intraday_manager import IntradayManager
from tests.testutils.apitest import APITest
from tests.factories.stock import StockFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory
from tests.factories.stock_price_chart import StockPriceChartFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory


class StockPriceRealtimeApiTestCase(APITest):
    def setUp(self):
        super(StockPriceRealtimeApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau")
        self.stock2 = StockFactory(symbol="VCB", name="Ngan hang vietcombank")

        datetime_now = datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))
        self.stock_price_1 = StockPriceRealtimeFactory(symbol="ACB", price=21.0, reference=20.0, datetime=datetime_now)
        self.stock_price_2 = StockPriceRealtimeFactory(symbol="VCB", price=80.0, datetime=datetime_now)

        StockPriceChartFactory(
            symbol="ACB",
            movement_1w="",
            movement_1m=[
                {"c": 18, "t": 123123}, {"c": 19, "t": 123123}, {"c": 20, "t": 123123}, {"c": 21, "t": 123123}
            ],
            movement_5y=[],
        )
        StockPriceChartFactory(
            symbol="VCB",
            movement_1w=[],
            movement_5y=[
                {"c": 81, "t": 123123}, {"c": 71, "t": 123123}, {"c": 72, "t": 123123}, {"c": 79, "t": 123123}
            ],
        )

        StockPriceAnalyticsFactory(symbol="ACB", price_1m=18)
        StockPriceAnalyticsFactory(symbol="VCB", price_5y=81)

        self.client = APIClient()

    @patch.object(IntradayManager, "get_and_build_chart_1d")
    @patch.object(IntradayManager, "get_price")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_db_success(self, init, get_price, charts):
        init.return_value = None
        time = datetime(2022, 12, 14, 14, 37, 40, tzinfo=tzoffset(None, 25200)).timestamp()
        get_price.return_value = 30.0, int(time)
        charts.return_value = [
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
        ]

        url = reverse('api:stock-price-realtime-detail', args=['ACB'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], 21.0)
        self.assertEqual(response.data['change_value'], 1.0)
        self.assertEqual(response.data['change_percentage'], 5.0)
        self.assertEqual(len(response.data['prices']), 4)

    @patch.object(IntradayManager, "get_and_build_chart_1d")
    @patch.object(IntradayManager, "get_price")
    @patch.object(IntradayManager, "__init__")
    def test_get_realtime_cache_success(self, init, get_price, charts):
        init.return_value = None
        time = datetime(2022, 12, 14, 14, 37, 49, tzinfo=tzoffset(None, 25200)).timestamp()
        charts.return_value = [
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
        ]
        get_price.return_value = 30.0, int(time)

        url = reverse('api:stock-price-realtime-detail', args=['ACB'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], 30.0)

    @patch.object(IntradayManager, "get_and_build_chart_1d")
    @patch.object(IntradayManager, "get_price")
    @patch.object(IntradayManager, "__init__")
    def test_get_failed(self, init, get_price, charts):
        init.return_value = None
        get_price.return_value = None, None
        charts.return_value = [
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
            {"o": 12.0, "h": 13.0, "l": 11.5, "c": 12.5, "v": 100,
             "t": datetime(2022, 12, 14, 14, 37, 43, tzinfo=tzoffset(None, 25200))},
        ]
        url = reverse('api:stock-price-realtime-detail', args=['XYZ'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse('api:stock-price-realtime-detail', args=['VCB'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['change_value'])
        self.assertIsNone(response.data['change_percentage'])

    @patch.object(IntradayManager, "get_and_build_chart_1d")
    @patch.object(IntradayManager, "get_price")
    @patch.object(IntradayManager, "__init__")
    def test_get_historical_range(self, init, get_price, charts):
        init.return_value = None
        get_price.return_value = None, None
        charts.return_value = []

        url = reverse('api:stock-price-realtime-detail', args=['ACB']) + "?date_range=1M"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['change_value'], 3.0)
        self.assertGreater(response.data['change_percentage'], 0)
        self.assertEqual(len(response.data['prices']), 5)
        self.assertIsNotNone(response.data['prices'][0]['c'])
        self.assertIsNotNone(response.data['prices'][0]['t'])

        url = reverse('api:stock-price-realtime-detail', args=['VCB']) + "?date_range=1Y"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['change_value'])
        self.assertIsNone(response.data['change_percentage'])
        self.assertEqual(response.data['prices'], [])
