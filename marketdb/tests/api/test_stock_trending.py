from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models.mixin import ContentStatusEnum
from tests.testutils.apitest import APITest
from tests.factories.stock import StockFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory
from core.models.stocks.stock import Stock


class StockTrendingTestCase(APITest):
    def setUp(self):
        super(StockTrendingTestCase, self).setUp()

        StockFactory(symbol="ACB", name="Ngan hang A Chau")
        StockFactory(symbol="VCB", name="Ngan hang vietcombank")
        StockFactory(symbol="MBB", name="Ngan hang MB Bank")

        self.stock1 = StockPriceRealtimeFactory(symbol="ACB", volume=10, total_trading_value=10)
        self.stock2 = StockPriceRealtimeFactory(symbol="VCB", volume=10, total_trading_value=7)
        self.stock3 = StockPriceRealtimeFactory(symbol="MBB", volume=10, total_trading_value=11)
        self.stock3 = StockPriceRealtimeFactory(symbol="XYZ", volume=0, total_trading_value=0)

        self.client = APIClient()

    def test_get_stocks_trending(self):
        url = reverse("api:trending-stocks")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["paging"]["count"], 3)
        self.assertEqual(response.data["items"][0]['symbol'], "MBB")
        self.assertEqual(response.data["items"][1]['symbol'], "ACB")
        self.assertEqual(response.data["items"][2]['symbol'], "VCB")
