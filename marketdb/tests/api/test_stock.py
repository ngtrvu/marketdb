from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models.mixin import ContentStatusEnum
from tests.testutils.apitest import APITest
from tests.factories.stock import StockFactory
from core.models.stocks.stock import Stock


class StockTestCase(APITest):
    def setUp(self):
        super(StockTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="acb", status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)
        self.stock2 = StockFactory(symbol="abc", status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)
        self.stock3 = StockFactory(symbol="xyz")
        self.client = APIClient()

    def test_get_stocks(self):
        url = reverse('api:stocks-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['paging']['count'], 2)

    def test_get_stock(self):
        url = reverse('api:stocks-detail', args=[self.stock2.symbol])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['symbol'])
        self.assertIsNotNone(response.data['name'])
        self.assertIsNotNone(response.data['exchange'])
        self.assertIsNotNone(response.data['photo'])
