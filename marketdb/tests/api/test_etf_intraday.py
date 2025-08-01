from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.libs.intraday.intraday_manager import IntradayManager
from tests.testutils.apitest import APITest
from tests.factories.etf import ETFFactory


class ETFIntradayApiTestCase(APITest):
    def setUp(self):
        super(ETFIntradayApiTestCase, self).setUp()

        self.stock1 = ETFFactory(symbol="ETF1", name="Ngan hang A Chau")
        self.stock2 = ETFFactory(symbol="ETF2", name="Ngan hang vietcombank")

        self.client = APIClient()

    @patch.object(IntradayManager, "get_and_build_chart_intraday")
    @patch.object(IntradayManager, "__init__")
    def test_get_intraday_results_success(self, init, order_stats):
        init.return_value = None
        order_stats.return_value = {'10.0': 100, '12.2': 200, '12.5': 150}

        url = reverse('api:etf-order-stats', args=['ETF1'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 3)
        self.assertEqual(response.data['items'][0]['price'], 10.0)
        self.assertEqual(response.data['items'][0]['volume'], 100.0)

    @patch.object(IntradayManager, "get_and_build_chart_intraday")
    @patch.object(IntradayManager, "__init__")
    def test_get_intraday_results_failed(self, init, order_stats):
        init.return_value = None
        order_stats.return_value = {}

        url = reverse('api:etf-order-stats', args=['XYZ'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('api:etf-order-stats', args=['ETF2'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], [])
