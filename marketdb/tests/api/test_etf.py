from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models.mixin import ContentStatusEnum
from tests.testutils.apitest import APITest
from tests.factories.etf import ETFFactory
from core.models.etfs.etf import ETF


class ETFTestCase(APITest):
    def setUp(self):
        super(ETFTestCase, self).setUp()

        self.etf1 = ETFFactory(symbol="ETFTestCase_ETFVN30", inav_symbol="ABC", status=ContentStatusEnum.PUBLISHED,
                               exchange_status=ETF.STATUS_LISTED)
        self.etf2 = ETFFactory(symbol="ETFTestCase_ETFVN31", inav_symbol="XYZ", status=ContentStatusEnum.PUBLISHED,
                               exchange_status=ETF.STATUS_LISTED)
        self.etf3 = ETFFactory(symbol="ETFTestCase_ETFVN32", inav_symbol="XYZ")
        self.client = APIClient()

    def test_get_etfs(self):
        url = reverse('api:etfs-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['paging']['count'], 2)

    def test_get_etf(self):
        url = reverse('api:etfs-detail', args=[self.etf2.symbol])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['symbol'])
        self.assertIsNotNone(response.data['inav_symbol'])
        self.assertIsNotNone(response.data['name'])
        self.assertIsNotNone(response.data['exchange'])
        self.assertIsNotNone(response.data['photo'])
        self.assertIsNotNone(response.data['id'])
