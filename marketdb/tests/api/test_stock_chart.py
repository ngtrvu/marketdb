from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.stock_price_realtime import StockPriceRealtimeFactory
from tests.testutils.apitest import APITest
from tests.factories.stock import StockFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_chart import StockPriceChartFactory


class StockPriceChartApiTestCase(APITest):
    def setUp(self):
        super(StockPriceChartApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau")
        self.stock2 = StockFactory(symbol="HPG", name="Tap doan Hoa Phat")
        self.stock2 = StockFactory(symbol="MBB", name="Ngan hang Quan Doi")

        StockPriceAnalyticsFactory(
            symbol="ACB", reference=20, price_1d=20, volume_1d=1000, fb_volume_1d=1000, fs_volume_1d=0,
            price_1w=20, price_1m=10, price_3m=15, price_6m=15, price_1y=40,
        )
        StockPriceAnalyticsFactory(symbol="HPG", reference=25, price_1d=25, volume_1d=2000, fb_volume_1d=2000,
                                   fs_volume_1d=0)

        StockPriceChartFactory(symbol="ACB")
        StockPriceChartFactory(symbol="HPG")

        StockPriceRealtimeFactory(symbol="ACB", price=21, volume=100)
        StockPriceRealtimeFactory(symbol="HPG", price=26, volume=100)

        self.client = APIClient()

    def test_get_stock_chart_success(self):
        url = reverse('api:stock-price-chart', args=['ACB'])
        url += "?date_range=1w"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], "ACB")
        self.assertEqual(response.data['date_range'], '1w')
        self.assertTrue('change_value' in response.data)
        self.assertTrue('change_percentage' in response.data)

    def test_get_stock_chart_failed(self):
        url = reverse('api:stock-price-chart', args=['XYZ'])
        url += "?date_range=1w"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('api:stock-price-chart', args=['MBB'])
        url += "?date_range=1w"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
