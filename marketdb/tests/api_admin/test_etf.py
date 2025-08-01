from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest
from core.models.etfs.etf import ETF
from tests.factories.etf import ETFFactory


class ETFTestCase(AdminAPITest):
    def setUp(self):
        super(ETFTestCase, self).setUp()

        self.etf1 = ETFFactory(name='E1VFVN30 VFM', symbol='E1VFVN30')
        self.etf2 = ETFFactory(name='FUEVFVND VFM', symbol='FUEVFVND')

    def test_get_etfs(self):
        url = reverse('api_admin:etf-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['name'], 'FUEVFVND VFM')
        self.assertEqual(response.data['items'][1]['name'], 'E1VFVN30 VFM')

    def test_get_etf(self):
        url = reverse('api_admin:etf-detail', args=[self.etf1.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['name'])

    def test_create_etf(self):
        url = reverse('api_admin:etf-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': 'E1VFMID VFM',
            'description': 'Description E1VFMID',
            'symbol': 'E1VFMID',
            'photo': self.generate_photo_file(),
            'exchange': 'hose',
            'reference_index': 'E1VFMID'
        }

        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = ETF.objects.all().count()
        self.assertEqual(count, 3)

        etf = ETF.objects.filter(symbol='E1VFMID').first()
        self.assertEqual(etf.name, 'E1VFMID VFM')
        self.assertEqual(etf.symbol, 'E1VFMID')
        self.assertEqual(etf.exchange, 'hose')

    def test_update_etf(self):
        data = {
            'name': 'E1VFVN30 DCVFM',
        }
        url = reverse('api_admin:etf-detail', args=[self.etf1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'E1VFVN30 DCVFM')

    def test_delete_etf(self):
        url = reverse('api_admin:etf-detail', args=[self.etf1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = ETF.objects.all().count()
        self.assertEqual(count, 1)
