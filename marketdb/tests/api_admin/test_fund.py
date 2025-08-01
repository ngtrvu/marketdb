from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest
from core.models.funds.fund import MutualFund
from tests.factories.fund import MutualFundFactory


class MutualFundTestCase(AdminAPITest):
    def setUp(self):
        super(MutualFundTestCase, self).setUp()

        self.fund1 = MutualFundFactory(name='DCDS VFM', symbol='DCDS')
        self.fund2 = MutualFundFactory(name='DCBC VFM', symbol='DCBC')

    def test_get_funds(self):
        url = reverse('api_admin:fund-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['name'], 'DCBC VFM')
        self.assertEqual(response.data['items'][1]['name'], 'DCDS VFM')

    def test_get_fund(self):
        url = reverse('api_admin:fund-detail', args=[self.fund1.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['name'])

    def test_create_fund(self):
        url = reverse('api_admin:fund-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': 'DCIP',
            'description': 'Description DCIP',
            'symbol': 'DCIP',
            'photo': self.generate_photo_file(),
        }

        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = MutualFund.objects.all().count()
        self.assertEqual(count, 3)

        fund = MutualFund.objects.filter(symbol='DCIP').first()
        self.assertEqual(fund.name, 'DCIP')
        self.assertEqual(fund.symbol, 'DCIP')

    def test_update_fund(self):
        data = {
            'name': 'DCDS DCVFM',
        }
        url = reverse('api_admin:fund-detail', args=[self.fund1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['symbol'])
        self.assertEqual(response.data['name'], 'DCDS DCVFM')

    def test_delete_fund(self):
        url = reverse('api_admin:fund-detail', args=[self.fund1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = MutualFund.objects.all().count()
        self.assertEqual(count, 1)
