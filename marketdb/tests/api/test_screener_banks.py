from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.bank import BankFactory


class ScreenerBanksApiTestCase(APITest):
    def setUp(self):
        super(ScreenerBanksApiTestCase, self).setUp()

        BankFactory(
            symbol="ACB", title="Ngan hang A Chau", slug='ngan-hang-acb',
            online_savings_1m=0.05,
            online_savings_3m=0.052,
            online_savings_6m=0.054,
            online_savings_9m=0.056,
            online_savings_12m=0.062,
            online_savings_24m=0.065,
            online_savings_36m=0.07,
        )
        BankFactory(
            symbol="MBB", title="Ngan hang quan doi", slug='ngan-hang-mbb',
            online_savings_1m=0.045,
            online_savings_3m=0.048,
            online_savings_6m=0.050,
            online_savings_9m=0.052,
            online_savings_12m=0.058,
            online_savings_24m=0.06,
            online_savings_36m=0.062,
        )
        BankFactory(
            symbol="VCB", title="Ngan hang VCB", slug='ngan-hang-vcb',
            online_savings_1m=0.040,
            online_savings_3m=0.042,
            online_savings_6m=0.046,
            online_savings_9m=0.050,
            online_savings_12m=0.054,
            online_savings_24m=0.058,
            online_savings_36m=0.06,
        )
        BankFactory(
            symbol="VPB", title="Ngan hang VPB", slug='ngan-hang-vpb',
            online_savings_1m=0.044,
            online_savings_3m=0.046,
            online_savings_6m=0.05,
            online_savings_9m=0.055,
            online_savings_12m=0.06,
            online_savings_24m=0.062,
            online_savings_36m=0.066,
        )

        self.client = APIClient()

    def test_get_screener_stocks(self):
        base_url = reverse('api:screener-banks')
        url = "{0}?fields=symbol,title,online_savings_6m,online_savings_12m&filters=online_savings_12m__gte__0.055&sorts=online_savings_12m__desc".format(base_url)
        response = self.client.get(url)

        self.assertEqual(response.data['paging']['count'], 3)

        self.assertEqual(response.data['items'][0]['symbol'], "ACB")
        self.assertEqual(response.data['items'][0]['title'], "Ngan hang A Chau")
        self.assertEqual(float(response.data['items'][0]['online_savings_6m']), 0.054)
        self.assertEqual(float(response.data['items'][0]['online_savings_12m']), 0.062)

        self.assertEqual(response.data['items'][1]['symbol'], "VPB")
        self.assertEqual(response.data['items'][1]['title'], "Ngan hang VPB")
        self.assertEqual(float(response.data['items'][1]['online_savings_6m']), 0.05)
        self.assertEqual(float(response.data['items'][1]['online_savings_12m']), 0.06)

        self.assertEqual(response.data['items'][2]['symbol'], "MBB")
        self.assertEqual(response.data['items'][2]['title'], "Ngan hang quan doi")
        self.assertEqual(float(response.data['items'][2]['online_savings_6m']), 0.05)
        self.assertEqual(float(response.data['items'][2]['online_savings_12m']), 0.058)
