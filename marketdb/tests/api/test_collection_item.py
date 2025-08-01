from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from core.models.screener.collection import ContentStatusEnum
from tests.factories.stock import StockFactory
from tests.factories.industry import IndustryFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory
from tests.factories.collection import CollectionFactory, MetricFactory


class CollectionItemsApiTestCase(APITest):

    def setUp(self):
        super(CollectionItemsApiTestCase, self).setUp()

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

        self.collection = CollectionFactory(
            title='Test collection', product_type='stock', status=ContentStatusEnum.PUBLISHED,
            field_params=['name', 'symbol', 'price', 'volume'],
            filter_params=[{'name': 'volume', 'operator': 'gt', 'value': 3000}],
            sort_params=[{'name': 'volume', 'type': 'desc'}],
            limit=20
        )

        MetricFactory(
            name='name', label='Name', product_type='stock', group='G1',
            source_model='Stock', source_field='name', data_type='string'
        )
        MetricFactory(
            name='symbol', label='Symbol', product_type='stock', group='G1',
            source_model='Stock', source_field='symbol', data_type='string'
        )
        MetricFactory(
            name='price', label='Price', product_type='stock', group='G1',
            source_model='StockPriceRealtime', source_field='price', data_type='currency'
        )
        MetricFactory(
            name='volume', label='Volume', product_type='stock', group='G1',
            source_model='StockPriceRealtime', source_field='volume', data_type='number'
        )

        self.client = APIClient()

    def test_get_collection_items(self):
        url = reverse('api:collection-detail-items', args=[self.collection.id])
        response = self.client.get(url)

        # MBB
        self.assertEqual(response.data['items'][0]['symbol'], "MBB")
        self.assertEqual(response.data['items'][0]['name'], "Ngan hang quan doi")

        self.assertEqual(response.data['items'][0]['metrics'][0]['key'], "name")
        self.assertEqual(response.data['items'][0]['metrics'][0]['label'], 'Name')
        self.assertEqual(response.data['items'][0]['metrics'][0]['value'], 'Ngan hang quan doi')
        self.assertEqual(response.data['items'][0]['metrics'][0]['type'], 'string')

        self.assertEqual(response.data['items'][0]['metrics'][1]['key'], "symbol")
        self.assertEqual(response.data['items'][0]['metrics'][1]['label'], 'Symbol')
        self.assertEqual(response.data['items'][0]['metrics'][1]['value'], 'MBB')
        self.assertEqual(response.data['items'][0]['metrics'][1]['type'], 'string')

        self.assertEqual(response.data['items'][0]['metrics'][2]['key'], "price")
        self.assertEqual(response.data['items'][0]['metrics'][2]['label'], 'Price')
        self.assertEqual(response.data['items'][0]['metrics'][2]['value'], 27)
        self.assertEqual(response.data['items'][0]['metrics'][2]['type'], 'currency')

        self.assertEqual(response.data['items'][0]['metrics'][3]['key'], "volume")
        self.assertEqual(response.data['items'][0]['metrics'][3]['label'], 'Volume')
        self.assertEqual(response.data['items'][0]['metrics'][3]['value'], 5500)
        self.assertEqual(response.data['items'][0]['metrics'][3]['type'], 'number')

        # VCB
        self.assertEqual(response.data['items'][1]['symbol'], "VCB")
        self.assertEqual(response.data['items'][1]['name'], "Ngan hang VCB")

        self.assertEqual(response.data['items'][1]['metrics'][0]['key'], "name")
        self.assertEqual(response.data['items'][1]['metrics'][0]['label'], 'Name')
        self.assertEqual(response.data['items'][1]['metrics'][0]['value'], 'Ngan hang VCB')
        self.assertEqual(response.data['items'][1]['metrics'][0]['type'], 'string')

        self.assertEqual(response.data['items'][1]['metrics'][1]['key'], "symbol")
        self.assertEqual(response.data['items'][1]['metrics'][1]['label'], 'Symbol')
        self.assertEqual(response.data['items'][1]['metrics'][1]['value'], 'VCB')
        self.assertEqual(response.data['items'][1]['metrics'][1]['type'], 'string')

        self.assertEqual(response.data['items'][1]['metrics'][2]['key'], "price")
        self.assertEqual(response.data['items'][1]['metrics'][2]['label'], 'Price')
        self.assertEqual(response.data['items'][1]['metrics'][2]['value'], 28)
        self.assertEqual(response.data['items'][1]['metrics'][2]['type'], 'currency')

        self.assertEqual(response.data['items'][1]['metrics'][3]['key'], "volume")
        self.assertEqual(response.data['items'][1]['metrics'][3]['label'], 'Volume')
        self.assertEqual(response.data['items'][1]['metrics'][3]['value'], 3500)
        self.assertEqual(response.data['items'][1]['metrics'][3]['type'], 'number')
