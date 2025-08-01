from django.test import TestCase

from core.services.stock.get_stock_chart import GetStockChartService
from tests.factories.stock import StockFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_chart import StockPriceChartFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory


class GetStockChartServiceTestCase(TestCase):
    def setUp(self):
        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau", exchange='hose')
        self.stock2 = StockFactory(symbol="HPG", name="HPG", exchange='hose')

        StockFAFactory(symbol="ACB", year=2022)
        StockFAFactory(symbol="HPG", year=2022)

        StockPriceAnalyticsFactory(
            symbol="ACB", reference=20, price_1d=20, price_1w=10, volume_1d=1000,
            fb_volume_1d=1000, fs_volume_1d=0,
        )
        StockPriceAnalyticsFactory(
            symbol="HPG", reference=25, price_1d=25, price_1w=15, volume_1d=2000,
            fb_volume_1d=2000, fs_volume_1d=0
        )

        StockPriceChartFactory(
            symbol="ACB", reference=20,
            movement_1w=[
                {"a": 10, "v": 100, "t": 1},
                {"a": 12, "v": 100, "t": 1},
                {"a": 14, "v": 100, "t": 1},
                {"a": 15, "v": 100, "t": 1},
            ])

        StockPriceRealtimeFactory(symbol="ACB", price=20, volume=1500, open=20, high=21.5, low=19, close=20)
        StockPriceRealtimeFactory(symbol="HPG", price=28, volume=2500, open=20, high=32, low=26, close=28)

        super(GetStockChartServiceTestCase, self).setUp()

    def test_get_stock_chart_data(self):

        get_chart = GetStockChartService(symbol='ACB', date_range='1w')
        success = get_chart.call()

        self.assertTrue(success)
        self.assertIsNotNone(get_chart.movement)
