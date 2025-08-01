from django.test import TestCase

from core.services.stock.get_stocks import GetStocksService
from tests.factories.stock import StockFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.industry import IndustryFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory


class GetStocksServiceTestCase(TestCase):
    def setUp(self):
        self.industry1 = IndustryFactory(name="ABC1", slug='abc1', level=1)
        self.industry2 = IndustryFactory(name="XYZ2", slug='xyz2', level=2)
        self.industry3 = IndustryFactory(name="ABC3", slug='abc3', level=3)
        self.industry4 = IndustryFactory(name="ABC4", slug='abc4', level=4, parent=self.industry3)
        self.industry5 = IndustryFactory(name="ABC5", slug='abc5', level=4, parent=self.industry3)

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau", exchange='hose',
                                   industry=self.industry1, super_sector=self.industry2, sector=self.industry3,
                                   sub_sector=self.industry4)
        self.stock2 = StockFactory(symbol="HPG", name="HPG", exchange='hose',
                                   industry=self.industry1, super_sector=self.industry2, sector=self.industry3,
                                   sub_sector=self.industry4)
        self.stock3 = StockFactory(symbol="MBB", name="Ngan hang quan doi", exchange='hose',
                                   industry=self.industry1, super_sector=self.industry2, sector=self.industry3,
                                   sub_sector=self.industry5)
        self.stock4 = StockFactory(symbol="VCB", name="Ngan hang VCB", exchange='hose',
                                   industry=self.industry1, super_sector=self.industry2, sector=self.industry3,
                                   sub_sector=self.industry5)

        StockFAFactory(symbol="ACB", year=2022)
        StockFAFactory(symbol="HPG", year=2022)
        StockFAFactory(symbol="MBB", year=2022)
        StockFAFactory(symbol="VCB", year=2022)

        StockPriceAnalyticsFactory(symbol="ACB", reference=20, price_1d=20, volume_1d=1000,
                                   fb_volume_1d=1000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="HPG", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=2000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="MBB", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=3000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="VCB", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=4000, fs_volume_1d=0)

        StockPriceRealtimeFactory(
            symbol="ACB", exchange='hose', type='stock', price=22, volume=1500, open=20, high=21.5, low=19, close=22)
        StockPriceRealtimeFactory(
            symbol="HPG", exchange='hose', type='stock', price=28, volume=2500, open=20, high=32, low=26, close=28)
        StockPriceRealtimeFactory(
            symbol="MBB", exchange='hose', type='stock', price=27, volume=5500, open=20, high=32, low=26, close=28)
        StockPriceRealtimeFactory(
            symbol="VCB", exchange='hose', type='stock', price=28, volume=2500, open=20, high=32, low=26, close=28)

        super(GetStocksServiceTestCase, self).setUp()

    def test_get_stocks_by_industry(self):
        filters = [
            {'name': 'sub_sector_id', 'operator': 'eq', 'value': self.industry5.pk},
            {'name': 'volume', 'operator': 'gt', 'value': 1500},
        ]
        sorts = [
            {'name': 'volume', 'type': 'desc'}
        ]
        fields = ['symbol', 'price', 'volume']
        result = GetStocksService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].symbol, "MBB")
        self.assertEqual(result[0].price, 27)
        self.assertEqual(result[0].volume, 5500)

        self.assertEqual(result[1].symbol, "VCB")
        self.assertEqual(result[1].price, 28)
        self.assertEqual(result[1].volume, 2500)

        # test get stock by super sector
        filters = [
            {'name': 'exchange', 'operator': 'eq', 'value': 'hose'},
            {'name': 'super_sector_id', 'operator': 'eq', 'value': self.industry2.pk},
        ]
        sorts = [
            {'name': 'volume', 'type': 'desc'}
        ]

        result = GetStocksService(filters=filters, sorts=sorts).call()
        self.assertEqual(len(result), 4)
