from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.market_index import MarketIndexFactory
from tests.factories.market_index_analytics import MarketIndexAnalyticsFactory


class ScreenerMarketIndexesApiTestCase(APITest):

    def setUp(self):
        super(ScreenerMarketIndexesApiTestCase, self).setUp()

        MarketIndexFactory(symbol="VN30", name='VN30')
        MarketIndexFactory(symbol="VNINDEX", name='VNIndex')

        MarketIndexAnalyticsFactory(symbol="VN30", close=1048.74, change_1d=-20, change_percentage_1d=-1.05)
        MarketIndexAnalyticsFactory(symbol="VNINDEX", close=1055.3, change_1d=-20, change_percentage_1d=-0.82)

        self.client = APIClient()

    def test_get_screener_market_indexes(self):
        base_url = reverse('api:screener-market-indexes')
        filter_config = "fields=symbol,close,change_1d,change_percentage_1d"
        url = f"{base_url}?{filter_config}"
        response = self.client.get(url)

        self.assertEqual(response.data['items'][0]['symbol'], "VNINDEX")
        self.assertEqual(float(response.data['items'][0]['change_percentage_1d']), -0.82)
        self.assertEqual(float(response.data['items'][0]['change_1d']), -20)

        self.assertEqual(response.data['items'][1]['symbol'], "VN30")
        self.assertEqual(float(response.data['items'][1]['change_percentage_1d']), -1.05)
        self.assertEqual(float(response.data['items'][1]['change_1d']), -20)
