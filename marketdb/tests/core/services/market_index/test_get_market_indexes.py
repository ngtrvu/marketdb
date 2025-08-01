from django.test import TestCase

from core.services.market_index.get_market_indexes import GetMarketIndexesService
from tests.factories.market_index import MarketIndexFactory
from tests.factories.market_index_analytics import MarketIndexAnalyticsFactory


class GetMarketIndexesServiceTestCase(TestCase):
    def setUp(self):
        MarketIndexFactory(symbol="VN30", name='VN30')
        MarketIndexFactory(symbol="VNINDEX", name='VNIndex')

        MarketIndexAnalyticsFactory(symbol="VN30", close=1048.74, change_1d=-20, change_percentage_1d=-1.05)
        MarketIndexAnalyticsFactory(symbol="VNINDEX", close=1055.3, change_1d=-20, change_percentage_1d=-0.82)

        super(GetMarketIndexesServiceTestCase, self).setUp()

    def test_get_market_indexes(self):
        filters = []
        sorts = []
        fields = ['name', 'symbol', 'change_percentage_1d', 'change_1d']
        result = GetMarketIndexesService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].symbol, "VNINDEX")
        self.assertEqual(float(result[0].change_percentage_1d), -0.82)
        self.assertEqual(float(result[0].change_1d), -20)

        self.assertEqual(result[1].symbol, "VN30")
        self.assertEqual(float(result[1].change_percentage_1d), -1.05)
        self.assertEqual(float(result[1].change_1d), -20)

