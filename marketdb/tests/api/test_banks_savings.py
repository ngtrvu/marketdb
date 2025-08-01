from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.bank import BankFactory


class BanksSavingsApiTestCase(APITest):
    def setUp(self):
        super(BanksSavingsApiTestCase, self).setUp()

        BankFactory(
            symbol="MBB", title="Ngan hang quan doi", slug='ngan-hang-mbb',
            online_savings_1m=0.045,
            online_savings_3m=0.048,
            online_savings_6m=0.050,
            online_savings_9m=0.052,
            online_savings_12m=0.058,
            online_savings_24m=0.06,
            online_savings_36m=0.062,
            capital_adequacy_ratio=0.28,
        )

        BankFactory(
            symbol="ACB", title="Ngan hang A Chau", slug='ngan-hang-acb',
            online_savings_1m=0.05,
            online_savings_3m=0.052,
            online_savings_6m=0.054,
            online_savings_9m=0.056,
            online_savings_12m=0.062,
            online_savings_24m=0.065,
            online_savings_36m=0.07,
            capital_adequacy_ratio=0.18,
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
            capital_adequacy_ratio=0.4,
        )

        BankFactory(
            symbol="VPB", title="Ngan hang VPB", slug='ngan-hang-vpb',
            online_savings_1m=0.044,
            online_savings_3m=0.046,
            online_savings_6m=0.05,
            online_savings_9m=None,
            online_savings_12m=0.06,
            online_savings_24m=0.062,
            online_savings_36m=0.066,
            capital_adequacy_ratio=0.22,
        )

        self.client = APIClient()

    def test_get_banks_savings_success(self):
        url = reverse('api:savings-banks') + '?savings_amount=100000000&savings_time=online_savings_9m&ordering=-capital_adequacy_ratio'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['items']), 4)

        self.assertEqual(response.data['items'][0]['symbol'], 'VCB')

        self.assertEqual(response.data['items'][1]['symbol'], 'MBB')

        self.assertEqual(response.data['items'][2]['symbol'], 'VPB')

        self.assertEqual(response.data['items'][3]['symbol'], 'ACB')

    def test_get_banks_savings_success_ordering(self):
        url = reverse('api:savings-banks') + '?savings_amount=100000000&savings_time=online_savings_9m'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['items']), 4)

        self.assertEqual(response.data['items'][0]['symbol'], 'ACB')
        self.assertEqual(float(response.data['items'][0]['savings_percentage']), 5.6)
        self.assertEqual(response.data['items'][0]['savings_month'], 9)
        self.assertEqual(float(response.data['items'][0]['profit']), 4200000)
        self.assertEqual(float(response.data['items'][0]['total']), 104200000)
        self.assertEqual(float(response.data['items'][0]['savings_percentage_detail']['online_savings_9m']), 5.6)

        self.assertEqual(response.data['items'][1]['symbol'], 'MBB')
        self.assertEqual(float(response.data['items'][1]['savings_percentage']), 5.2)
        self.assertEqual(response.data['items'][1]['savings_month'], 9)
        self.assertEqual(float(response.data['items'][1]['profit']), 3900000)
        self.assertEqual(float(response.data['items'][1]['total']), 103900000)
        self.assertEqual(float(response.data['items'][1]['savings_percentage_detail']['online_savings_9m']), 5.2)

        self.assertEqual(response.data['items'][2]['symbol'], 'VCB')
        self.assertEqual(float(response.data['items'][2]['savings_percentage']), 5.0)
        self.assertEqual(response.data['items'][2]['savings_month'], 9)
        self.assertEqual(float(response.data['items'][2]['profit']), 3750000)
        self.assertEqual(float(response.data['items'][2]['total']), 103750000)
        self.assertEqual(float(response.data['items'][2]['savings_percentage_detail']['online_savings_9m']), 5)

        self.assertEqual(response.data['items'][3]['symbol'], 'VPB')
        self.assertEqual(response.data['items'][3]['savings_percentage'], None)
        self.assertEqual(response.data['items'][3]['savings_month'], 9)
        self.assertEqual(response.data['items'][3]['profit'], None)
        self.assertEqual(response.data['items'][3]['total'], None)
        self.assertEqual(response.data['items'][3]['savings_percentage_detail']['online_savings_9m'], None)

    def test_get_banks_savings_fail(self):
        # fail
        url = reverse('api:savings-banks') + '?savings_amount=100000000&savings_time=online_savings_91m'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

        # fail
        url = reverse('api:savings-banks') + '?savings_time=online_savings_9m'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

