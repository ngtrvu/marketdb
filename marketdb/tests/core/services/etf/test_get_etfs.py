from django.test import TestCase

from core.services.etf.get_etfs import GetETFsService
from tests.factories.etf import ETFFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory


class GetETFsServiceTestCase(TestCase):
    def setUp(self):
        ETFFactory(symbol="E1VFVN30", name="Quy E1VFVN30", exchange='hose')
        ETFFactory(symbol="FUEVFVND", name="Quy FUEVFVND", exchange='hose')
        ETFFactory(symbol="FUEVN100", name="Quy FUEVN100", exchange='hose')

        StockFAFactory(symbol="E1VFVN30", year=2022, market_cap=1000000000, pe=4)
        StockFAFactory(symbol="FUEVFVND", year=2022, market_cap=900000000, pe=3)
        StockFAFactory(symbol="FUEVN100", year=2022, market_cap=800000000, pe=3.5)

        StockPriceAnalyticsFactory(
            symbol="E1VFVN30", reference=20000, price_1d=20000, volume_1d=1000,
            fb_volume_1d=1000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(
            symbol="FUEVFVND", reference=25000, price_1d=25000, volume_1d=2000,
            fb_volume_1d=2000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(
            symbol="FUEVN100", reference=25000, price_1d=25000, volume_1d=2000,
            fb_volume_1d=3000, fs_volume_1d=0)

        StockPriceRealtimeFactory(
            symbol="E1VFVN30", price=22000, volume=1500, open=20000, high=21500, low=19000,
            close=22000)
        StockPriceRealtimeFactory(
            symbol="FUEVFVND", price=28000, volume=2500, open=20000, high=32000, low=26000,
            close=28000)
        StockPriceRealtimeFactory(
            symbol="FUEVN100", price=27000, volume=5500, open=20000, high=32000, low=26000,
            close=28000)

        super(GetETFsServiceTestCase, self).setUp()

    def test_get_etfs(self):
        filters = [
            {'name': 'pe', 'operator': 'gt', 'value': 3},
        ]
        sorts = [
            {'name': 'market_cap', 'type': 'asc'}
        ]
        fields = ['symbol', 'price', 'volume']
        result = GetETFsService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(result[1].symbol, "FUEVN100")
        self.assertEqual(result[1].price, 27000)
        self.assertEqual(result[1].volume, 5500)

        self.assertEqual(result[0].symbol, "E1VFVN30")
        self.assertEqual(result[0].price, 22000)
        self.assertEqual(result[0].volume, 1500)

        self.assertEqual(len(result), 2)
