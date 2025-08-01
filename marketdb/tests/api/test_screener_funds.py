from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.fund import MutualFundFactory
from tests.factories.fund_price_index import FundPriceIndexFactory


class ScreenerFundsApiTestCase(APITest):
    def setUp(self):
        super(ScreenerFundsApiTestCase, self).setUp()

        MutualFundFactory(symbol="DCDS", name="Quy DCDS")
        MutualFundFactory(symbol="DCBF", name="Quy DCBF")
        MutualFundFactory(symbol="VFF", name="Quy FUEVN100")

        FundPriceIndexFactory(symbol="DCDS", nav=22000, total_nav=1000000000)
        FundPriceIndexFactory(symbol="DCBF", nav=18000, total_nav=800000000)
        FundPriceIndexFactory(symbol="VFF", nav=30000, total_nav=500000000)

        self.client = APIClient()

    def test_get_screener_stocks(self):
        base_url = reverse('api:screener-funds')
        url = "{0}?fields=symbol,nav,total_nav&filters=nav__gte__20000,total_nav__gte__500000000&sorts=total_nav__asc".format(base_url)
        response = self.client.get(url)

        self.assertEqual(response.data['paging']['count'], 2)

        self.assertEqual(response.data['items'][0]['symbol'], "VFF")
        self.assertEqual(response.data['items'][0]['nav'], 30000)
        self.assertEqual(response.data['items'][0]['total_nav'], 500000000)

        self.assertEqual(response.data['items'][1]['symbol'], "DCDS")
        self.assertEqual(response.data['items'][1]['nav'], 22000)
        self.assertEqual(response.data['items'][1]['total_nav'], 1000000000)
