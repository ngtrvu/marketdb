from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.stock import StockFactory
from tests.factories.industry import IndustryFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory


class ScreenerStocksApiTestCase(APITest):

    def setUp(self):
        super(ScreenerStocksApiTestCase, self).setUp()

        industry1 = IndustryFactory(name="ABC1", slug='abc1', level=1)
        industry2 = IndustryFactory(name="XYZ2", slug='xyz2', level=2, parent=industry1)
        industry3 = IndustryFactory(name="ABC3", slug='abc3', level=3, parent=industry2)
        industry4 = IndustryFactory(name="ABC4", slug='abc4', level=4, parent=industry3)

        StockFactory(symbol="ACB", name="Ngan hang A Chau", exchange='hose',
                     industry=industry1, super_sector=industry2, sector=industry3, sub_sector=industry4)
        StockFactory(symbol="HPG", name="HPG", exchange='hose',
                     industry=industry1, super_sector=industry2, sector=industry3, sub_sector=industry4)
        StockFactory(symbol="MBB", name="Ngan hang quan doi", exchange='hose',
                     industry=industry1, super_sector=industry2, sector=industry3, sub_sector=industry4)
        StockFactory(symbol="VCB", name="Ngan hang VCB", exchange='hose',
                     industry=industry1, super_sector=industry2, sector=industry3, sub_sector=industry4)
        StockFactory(symbol="ANT", name="CTCP Rau quả Thực phẩm An Giang", exchange='upcom',
                     industry=industry1, super_sector=industry2, sector=industry3, sub_sector=industry4)

        StockFAFactory(symbol="ACB", year=2022)
        StockFAFactory(symbol="HPG", year=2022)
        StockFAFactory(symbol="MBB", year=2022)
        StockFAFactory(symbol="VCB", year=2022)
        StockFAFactory(symbol="ANT", year=2022)

        StockPriceAnalyticsFactory(symbol="ACB", reference=20, price_1d=20, volume_1d=1000,
                                   fb_volume_1d=1000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="HPG", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=2000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="MBB", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=3000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="VCB", reference=25, price_1d=25, volume_1d=2000,
                                   fb_volume_1d=4000, fs_volume_1d=0)
        StockPriceAnalyticsFactory(symbol="ANT", reference=35, price_1d=35, volume_1d=4000,
                                   fb_volume_1d=400, fs_volume_1d=0)

        StockPriceRealtimeFactory(
            symbol="ACB", exchange='hose', type='stock', price=22, volume=1500, open=20, high=21.5, low=19, close=22)
        StockPriceRealtimeFactory(
            symbol="HPG", exchange='hose', type='stock', price=28, volume=2500, open=20, high=32, low=26, close=28)
        StockPriceRealtimeFactory(
            symbol="MBB", exchange='hose', type='stock', price=27, volume=5500, open=20, high=32, low=26, close=28)
        StockPriceRealtimeFactory(
            symbol="VCB", exchange='hose', type='stock', price=28, volume=3500, open=20, high=32, low=26, close=28)
        StockPriceRealtimeFactory(
            symbol="ANT", exchange='upcom', type='stock', price=35, volume=2500, open=30, high=40, low=33, close=35)

        self.client = APIClient()

    def test_get_screener_stocks(self):
        base_url = reverse('api:screener-stocks')
        filter_config = "fields=symbol,price,fb_volume_1d&filters=exchange__eq__hose,volume__gte__2500&sorts=volume__desc"
        url = f"{base_url}?{filter_config}"
        response = self.client.get(url)

        self.assertEqual(response.data['paging']['count'], 3)
        self.assertEqual(response.data['items'][0]['symbol'], "MBB")
        self.assertEqual(response.data['items'][0]['price'], 27)
        self.assertEqual(response.data['items'][0]['fb_volume_1d'], 3000)

        self.assertEqual(response.data['items'][1]['symbol'], "VCB")
        self.assertEqual(response.data['items'][1]['price'], 28)
        self.assertEqual(response.data['items'][1]['fb_volume_1d'], 4000)

        self.assertEqual(response.data['items'][2]['symbol'], "HPG")
        self.assertEqual(response.data['items'][2]['price'], 28)
        self.assertEqual(response.data['items'][2]['fb_volume_1d'], 2000)
