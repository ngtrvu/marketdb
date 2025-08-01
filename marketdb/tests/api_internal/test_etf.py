from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.etf import ETFFactory
from tests.testutils.apitest import APITest


class ETFApiInternalTestCase(APITest):
    def setUp(self):
        super(ETFApiInternalTestCase, self).setUp()

        self.etf1 = ETFFactory(symbol="FUEDCMID", name="Quỹ ETF DCVFMVN MIDCAPk")
        self.etf2 = ETFFactory(symbol="FUEVN100", name="Quỹ ETF VINACAPITAL VN100")

        self.client = APIClient()

    def test_get_internal_etf_list_success(self):
        url = reverse("api_internal:etf-list")
                
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['symbol'], self.etf1.symbol)
        self.assertEqual(response.data[1]['symbol'], self.etf2.symbol)

    def test_get_internal_etf_detail_success(self):
        url = reverse("api_internal:etf-detail", args=[self.etf2.symbol])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "FUEVN100")

    def test_get_internal_etf_detail_have_no_data(self):
        url = reverse("api_internal:etf-detail", args=["XYZ"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
